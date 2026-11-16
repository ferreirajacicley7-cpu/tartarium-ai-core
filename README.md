# TARTARIUM AI // SCIENCE_AI_BOX CORE

**Núcleo Soberano de Textualidade, Silos Estanques Dewey e Protocolo Theatre of Veritas (ToV)**

A **Tartarium AI** é uma arquitetura *self-hosted* projetada para processamento textual de alta precisão sem depender de APIs proprietárias externas. O ecossistema fundamenta-se nos critérios de textualidade de **Beaugrande & Dressler**, no isolamento físico de dados via **Silos Estanques Dewey** e na auditoria criptográfica **Theatre of Veritas (ToV)**.

---

## Diferenciais Arquiteturais

* **Soberania e Execução Local (Edge / VPS):** Opera sobre modelos otimizados de 7 bilhões de parâmetros (7B QLoRA), eliminando custos recorrentes por token externo e vazamento de contexto.
* **Silos Estanques Dewey:** Particionamento lógico e físico dos diretórios de dados por domínio do conhecimento (`000` a `800`), reduzindo o atrito de I/O e impedindo contaminação semântica.
* **Protocolo Theatre of Veritas (ToV):** Separação estrita entre o modo de simulação (`SANDBOX`) e o modo de produção auditável (`VERITAS`), gerando elos unívocos **SHA-256** (`SCI_...`) para cada artefato registrado.
* **ScienceAI_Box Public Repository:** Motor de indexação e certificação de teses e descobertas científicas com renderização de *Model Cards* em interface **Púrpura Cyberpunk & Esmeralda**.
* **Ledger Soberano Integrado:** Contabilização nativa de créditos computacionais (`tartarium_ledger.py`) para controle de consumo e monetização de acessos.

---

## Estrutura do Repositório

| Arquivo | Função no Ecossistema |
| :--- | :--- |
| `main.py` | Servidor **FastAPI** principal com as rotas da `Prompt_Box`, `ScienceAI_Box` e entrega da interface web. |
| `tartarium_ledger.py` | Módulo de contabilização de créditos (`SANDBOX` e `VERITAS`) com recibos auditáveis em SHA-256. |
| `index.html` | Console público responsivo com identidade visual **Púrpura Cyberpunk & Esmeralda**. |
| `requirements.txt` | Dependências Python necessárias para levantar o servidor. |
| `.env.example` | Modelo de variáveis de ambiente para configuração de chaves e diretórios locais. |

---

## Instalação e Execução Rápida

### 1. Clonar o Repositório
```bash
git clone [https://github.com/ferreirajacicley7-cpu/tartarium-ai-core.git](https://github.com/ferreirajacicley7-cpu/tartarium-ai-core.git)
cd tartarium-ai-core
