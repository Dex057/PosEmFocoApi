import secrets
import threading

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext

from app.dao.usuario_dao import UsuarioDAO
from app.dao.interesse_dao import InteresseDAO
from app.dao.edital_dao import EditalDAO
from app.services.scraper import executar_scraper

app = FastAPI(title="PósEmFoco")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha_pura: str, senha_hash: str):
    return pwd_context.verify(senha_pura, senha_hash)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

usuario_dao = UsuarioDAO()
interesse_dao = InteresseDAO()
edital_dao = EditalDAO()

# ponytail: sessões em memória — somem no restart e não valem para múltiplos workers.
# Trocar por JWT ou tabela de sessão quando sair do MVP.
SESSOES: dict[str, int] = {}

# ponytail: lock global de processo — só impede o scraper rodar duas vezes nesta instância.
# Com mais de um container, usar advisory lock do Postgres.
_lock_scraper = threading.Lock()


def usuario_logado(authorization: str = Header(None)) -> int:
    token = (authorization or "").removeprefix("Bearer ").strip()
    usuario_id = SESSOES.get(token)
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Sessão expirada. Faça login novamente.")
    return usuario_id


def rodar_scraper_uma_vez():
    if not _lock_scraper.acquire(blocking=False):
        print("Scraper já está rodando, ignorando novo disparo.")
        return
    try:
        executar_scraper()
    finally:
        _lock_scraper.release()


class UsuarioInput(BaseModel):
    nome: str
    email: str
    senha: str
    nivel_graduacao: str
    interesses: List[str] = []

class LoginInput(BaseModel):
    email: str
    senha: str

class InteressesInput(BaseModel):
    interesses: List[str]

class EditalInput(BaseModel):
    titulo: str
    link: str
    resumo: Optional[str] = None
    data_publicacao: Optional[str] = None


@app.get("/")
def home():
    return RedirectResponse("/frontend/login.html")

@app.get("/health")
def health():
    return {"mensagem": "API PósEmFoco rodando com PostgreSQL"}

@app.post("/cadastro")
def cadastrar(dados: UsuarioInput):
    if len(dados.senha) < 6:
        raise HTTPException(status_code=400, detail="A senha precisa ter no mínimo 6 caracteres.")

    if usuario_dao.buscar_por_email(dados.email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    class UsuarioParaSalvar:
        def __init__(self, d):
            self.nome = d.nome
            self.email = d.email
            self.senha_hash = gerar_hash(d.senha)
            self.nivel_graduacao = d.nivel_graduacao

    novo_usuario = UsuarioParaSalvar(dados)

    usuario_id = usuario_dao.salvar(novo_usuario)

    if not usuario_id:
        raise HTTPException(status_code=500, detail="Erro interno ao cadastrar usuário.")

    if dados.interesses:
        interesse_dao.substituir(usuario_id, dados.interesses)

    return {"mensagem": "Usuário cadastrado com sucesso!", "id": usuario_id}

@app.post("/login")
def login(dados: LoginInput):
    usuario_encontrado = usuario_dao.buscar_por_email(dados.email)

    if not usuario_encontrado:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    senha_valida = verificar_senha(dados.senha, usuario_encontrado['senha_hash'])

    if not senha_valida:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    token = secrets.token_urlsafe(32)
    SESSOES[token] = usuario_encontrado['id']

    return {
        "mensagem": "Login realizado com sucesso.",
        "token": token,
        "usuario": {
            "id": usuario_encontrado['id'],
            "nome": usuario_encontrado['nome'],
            "email": usuario_encontrado['email'],
            "nivel_graduacao": usuario_encontrado['nivel_graduacao']
        }
    }

@app.get("/editais")
def listar_editais():
    return edital_dao.listar_todos()

@app.get("/me/editais")
def listar_meus_editais(usuario_id: int = Depends(usuario_logado)):
    palavras = interesse_dao.listar_por_usuario(usuario_id)
    if not palavras:
        return []
    return edital_dao.listar_por_palavras(palavras)

@app.get("/me/interesses")
def listar_meus_interesses(usuario_id: int = Depends(usuario_logado)):
    return interesse_dao.listar_por_usuario(usuario_id)

@app.put("/me/interesses")
def atualizar_meus_interesses(dados: InteressesInput, usuario_id: int = Depends(usuario_logado)):
    palavras = [p.strip() for p in dados.interesses if p.strip()]
    if not interesse_dao.substituir(usuario_id, palavras):
        raise HTTPException(status_code=500, detail="Erro ao salvar interesses.")
    return palavras

@app.post("/scraper/rodar")
def disparar_scraper(background_tasks: BackgroundTasks, usuario_id: int = Depends(usuario_logado)):
    background_tasks.add_task(rodar_scraper_uma_vez)
    return {"mensagem": "Busca iniciada. Os novos editais aparecem aqui em alguns minutos."}

@app.post("/editais")
def salvar_edital(edital: EditalInput):
    if edital_dao.salvar(edital.dict()):
        return {"mensagem": "Edital salvo com sucesso"}
    return {"mensagem": "Edital não salvo (provavelmente duplicado)"}
