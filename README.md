# Autopeças - FastAPI

API e UI simples para gestão de autopeças, fornecedores, clientes, compras, vendas e estoque.

## Requisitos
- Python 3.11+

## Instalação

Caso `venv` não esteja disponível, instale dependências no usuário:

```bash
python3 -m pip install --user -r requirements.txt
```

Se preferir venv (em sistemas com `python3-venv`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar

Crie o arquivo `.env` (opcional):

```env
SECRET_KEY=uma-chave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=480
DATABASE_URL=sqlite+aiosqlite:///./app.db
DEBUG=true
```

Inicie o servidor:

```bash
uvicorn app.main:app --reload
```

Endpoints úteis:
- `GET /health`
- `POST /auth/register`
- `POST /auth/token` (OAuth2 password)
- CRUD: `/parts`, `/suppliers`, `/customers`
- Movimentações: `POST /transactions/purchases`, `POST /transactions/sales`
- UI: `/` e `/ui/parts`

## Testes

```bash
pytest -q
```