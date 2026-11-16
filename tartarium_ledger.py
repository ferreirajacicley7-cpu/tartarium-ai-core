import os
import json
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

ledger_router = APIRouter(prefix="/api/v1/ledger", tags=["Ledger & Monetização"])

BASE_SILOS = os.getenv("TARTARIUM_SILOS_DIR", "./data/silos")
LEDGER_DIR = os.path.join(BASE_SILOS, "300_legislacao", "ledger_contas")
os.makedirs(LEDGER_DIR, exist_ok=True)

TABELA_CUSTOS = {
    "prompt_infer_7b": 1.0,
    "science_box_unlock": 5.0,
    "gateway_p2p_dispatch": 2.0
}

class RecargaInput(BaseModel):
    conta_id: str
    valor_creditos: float
    tx_hash_ou_comprovante: str
    tov_mode: str = "SANDBOX"

class ConsumoInput(BaseModel):
    conta_id: str
    operacao: str
    artefato_ref: str = "GERAL"

def _carregar_conta(conta_id: str) -> dict:
    safe_id = "".join(c for c in conta_id if c.isalnum() or c in ("_", "-"))
    path = os.path.join(LEDGER_DIR, f"{safe_id}.json")
    if not os.path.exists(path):
        return {
            "conta_id": safe_id,
            "saldo_veritas": 0.0,
            "saldo_sandbox": 100.0,
            "historico_hashes": []
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _salvar_conta(conta_data: dict):
    path = os.path.join(LEDGER_DIR, f"{conta_data['conta_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(conta_data, f, ensure_ascii=False, indent=4)

@ledger_router.post("/recarregar")
def registrar_recarga(data: RecargaInput):
    conta = _carregar_conta(data.conta_id)
    timestamp = datetime.now(timezone.utc).isoformat()
    mode = data.tov_mode.upper()

    if mode == "VERITAS":
        conta["saldo_veritas"] += data.valor_creditos
    else:
        conta["saldo_sandbox"] += data.valor_creditos

    raw_tx = f"RECARGA|{conta['conta_id']}|{data.valor_creditos}|{data.tx_hash_ou_comprovante}|{timestamp}"
    tx_elo = f"TX_{hashlib.sha256(raw_tx.encode('utf-8')).hexdigest()[:16].upper()}"

    conta["historico_hashes"].append({
        "tx_elo": tx_elo,
        "tipo": "RECARGA",
        "modo": mode,
        "valor": data.valor_creditos,
        "comprovante": data.tx_hash_ou_comprovante,
        "timestamp_utc": timestamp
    })
    _salvar_conta(conta)

    return {
        "status": "CREDITADO",
        "tx_elo": tx_elo,
        "saldo_veritas": conta["saldo_veritas"],
        "saldo_sandbox": conta["saldo_sandbox"]
    }

@ledger_router.post("/consumir")
def debitar_operacao(data: ConsumoInput, tov_mode: str = "SANDBOX"):
    custo = TABELA_CUSTOS.get(data.operacao)
    if custo is None:
        raise HTTPException(status_code=400, detail="Operação não tarifada.")

    conta = _carregar_conta(data.conta_id)
    mode = tov_mode.upper()
    campo_saldo = "saldo_veritas" if mode == "VERITAS" else "saldo_sandbox"

    if conta[campo_saldo] < custo:
        raise HTTPException(status_code=402, detail=f"Saldo insuficiente ({mode}).")

    conta[campo_saldo] -= custo
    timestamp = datetime.now(timezone.utc).isoformat()
    raw_tx = f"DEBITO|{conta['conta_id']}|{data.operacao}|{custo}|{data.artefato_ref}|{timestamp}"
    tx_elo = f"TX_{hashlib.sha256(raw_tx.encode('utf-8')).hexdigest()[:16].upper()}"

    conta["historico_hashes"].append({
        "tx_elo": tx_elo,
        "tipo": "CONSUMO",
        "operacao": data.operacao,
        "artefato": data.artefato_ref,
        "custo": custo,
        "timestamp_utc": timestamp
    })
    _salvar_conta(conta)

    return {
        "status": "AUTORIZADO",
        "tx_elo": tx_elo,
        "custo_debitado": custo,
        "saldo_restante": conta[campo_saldo]
    }
