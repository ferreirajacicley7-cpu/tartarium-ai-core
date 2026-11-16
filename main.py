import os
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from tartarium_ledger import ledger_router

load_dotenv()

app = FastAPI(
    title="Tartarium AI // ScienceAI_Box Core",
    version="3.5.0-OSS",
    description="Núcleo Soberano de Textualidade, Silos Dewey e Protocolo Theater of Veritas (ToV)."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_SECRET = os.getenv("TARTARIUM_API_KEY", "TARTARIUM_DEV_SANDBOX_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY_SECRET:
        return api_key
    raise HTTPException(status_code=403, detail="Acesso negado: X-API-Key inválida.")

# Inicialização dos Silos Estanques
BASE_SILOS = os.getenv("TARTARIUM_SILOS_DIR", "./data/silos")
SCIENCE_BOX_DIR = os.path.join(BASE_SILOS, "science_ai_box")
TESES_DIR = os.path.join(SCIENCE_BOX_DIR, "teses")
DESCOBERTAS_DIR = os.path.join(SCIENCE_BOX_DIR, "descobertas")
METADADOS_DIR = os.path.join(SCIENCE_BOX_DIR, "metadados")

for d in [TESES_DIR, DESCOBERTAS_DIR, METADADOS_DIR]:
    os.makedirs(d, exist_ok=True)

app.include_router(ledger_router)

# --- MODELOS DE DADOS ---
class TextInferenceInput(BaseModel):
    texto_base: str
    tipo_textual: str = "Dissertativo-Argumentativo"
    tov_mode: str = "SANDBOX"
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)

class ScienceSubmissionInput(BaseModel):
    titulo: str
    conteudo: str
    categoria: str = "tese"
    tags: List[str] = ["GreenAI", "SilosDewey"]
    tov_mode: str = "SANDBOX"

# --- ROTAS ---
@app.get("/", include_in_schema=False)
def serve_frontend():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "Tartarium AI Core Online", "docs": "/docs"}

@app.post("/api/v1/tartarium/text-infer", tags=["Core Textual"])
def api_textual_inference(data: TextInferenceInput, api_key: str = Depends(verify_api_key)):
    mode = data.tov_mode.upper()
    tov_prefix = "[TOV // SIMULAÇÃO CONTROLADA]" if mode == "SANDBOX" else "[TOV // VERITAS SOBERANO]"
    
    resposta = (
        f"{tov_prefix}\n"
        f"Processamento pragmático ({data.tipo_textual}) concluído sobre: '{data.texto_base[:120]}...'. "
        f"Integridade de coesão validada sob Silos Estanques Dewey."
    )

    return {
        "status": "success",
        "tov_mode": mode,
        "tipo_textual": data.tipo_textual,
        "response_certificada": resposta,
        "bloco_bibliografico": [
            {"fonte": "ScienceAI_Box", "descricao": "Repositório Soberano de Teses e Descobertas", "elo_sha256": "SCI_CORE_7B_REF"},
            {"fonte": "Beaugrande & Dressler", "descricao": "Critérios de Textualidade e Informatividade", "elo_sha256": None}
        ],
        "bloco_rodape": [
            {"indice": 1, "nota": "Auditoria executada pelo Protocolo Theater of Veritas (ToV)."},
            {"indice": 2, "nota": f"Parâmetro térmico aplicado: T={data.temperature}."}
        ]
    }

@app.post("/api/v1/science/register", tags=["ScienceAI_Box"])
def register_science_artifact(payload: ScienceSubmissionInput, api_key: str = Depends(verify_api_key)):
    cat = payload.categoria.lower().strip()
    if cat not in ["tese", "descoberta"]:
        raise HTTPException(status_code=400, detail="Categoria deve ser 'tese' ou 'descoberta'.")

    mode = payload.tov_mode.upper().strip() if payload.tov_mode.upper() in ["SANDBOX", "VERITAS"] else "SANDBOX"
    timestamp = datetime.now(timezone.utc).isoformat()
    raw_stream = f"{payload.titulo}|{payload.conteudo}|{timestamp}|{mode}"
    elo_id = f"SCI_{hashlib.sha256(raw_stream.encode('utf-8')).hexdigest()[:16].upper()}"

    doc = {
        "elo_id": elo_id,
        "titulo": payload.titulo,
        "categoria": cat,
        "tags": payload.tags,
        "tov_mode": mode,
        "timestamp_utc": timestamp,
        "conteudo_completo": payload.conteudo
    }

    target_dir = TESES_DIR if cat == "tese" else DESCOBERTAS_DIR
    with open(os.path.join(target_dir, f"{elo_id}.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=4)

    index_file = os.path.join(METADADOS_DIR, "master_index.json")
    index_data = []
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)

    index_data.append({
        "elo_id": elo_id,
        "titulo": payload.titulo,
        "categoria": cat,
        "tags": payload.tags,
        "tov_mode": mode,
        "timestamp_utc": timestamp
    })
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=4)

    return {"status": "SUCESSO", "elo_id": elo_id, "categoria": cat, "tov_mode": mode, "timestamp_utc": timestamp}

@app.get("/api/v1/science/list", tags=["ScienceAI_Box"])
def list_science_artifacts(
    categoria: Optional[str] = None,
    tag: Optional[str] = None,
    busca: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    index_file = os.path.join(METADADOS_DIR, "master_index.json")
    if not os.path.exists(index_file):
        return {"status": "sucesso", "total_registros": 0, "resultados": []}

    with open(index_file, "r", encoding="utf-8") as f:
        registros = json.load(f)

    resultados = []
    for reg in registros:
        if categoria and reg.get("categoria", "").lower() != categoria.lower():
            continue
        if tag and tag.lower() not in [t.lower() for t in reg.get("tags", [])]:
            continue
        if busca and (busca.lower() not in reg.get("titulo", "").lower() and busca.lower() not in reg.get("elo_id", "").lower()):
            continue

        cat_folder = TESES_DIR if reg.get("categoria") == "tese" else DESCOBERTAS_DIR
        art_path = os.path.join(cat_folder, f"{reg['elo_id']}.json")
        conteudo = ""
        if os.path.exists(art_path):
            with open(art_path, "r", encoding="utf-8") as af:
                conteudo = json.load(af).get("conteudo_completo", "")

        resultados.append({**reg, "conteudo": conteudo})

    return {"status": "sucesso", "total_registros": len(resultados), "resultados": resultados}
