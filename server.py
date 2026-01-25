from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext  

from app.dao.usuario_dao import UsuarioDAO
from app.dao.interesse_dao import InteresseDAO
from app.dao.edital_dao import EditalDAO
from app.services.scraper import executar_scraper

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha_pura: str, senha_hash: str):
    return pwd_context.verify(senha_pura, senha_hash)


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

usuario_dao = UsuarioDAO()
interesse_dao = InteresseDAO()
edital_dao = EditalDAO()

class UsuarioInput(BaseModel):
    nome: str
    email: str
    senha: str
    nivel_graduacao: str
    interesses: List[str] = []

class LoginInput(BaseModel):
    email: str
    senha: str

class EditalInput(BaseModel):
    titulo: str
    link: str
    resumo: Optional[str] = None
    data_publicacao: Optional[str] = None


@app.get("/")
def home():
    return {"mensagem": "API PósEmFoco rodando com PostgreSQL"}

@app.post("/cadastro")
def cadastrar(dados: UsuarioInput):
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

    if usuario_id:
        if dados.interesses:
            interesse_dao.salvar_lista(usuario_id, dados.interesses)
        
        return {"mensagem": "Usuário cadastrado com sucesso!", "id": usuario_id}
    else:
        raise HTTPException(status_code=500, detail="Erro interno ao cadastrar usuário.")

@app.post("/login")
def login(dados: LoginInput, background_tasks: BackgroundTasks):
    usuario_encontrado = usuario_dao.buscar_por_email(dados.email)

    if not usuario_encontrado:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    senha_valida = verificar_senha(dados.senha, usuario_encontrado['senha_hash'])

    if not senha_valida:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    print(f"Login efetuado por {usuario_encontrado['nome']}. Iniciando atualização de editais...")
    background_tasks.add_task(executar_scraper)

    return {
        "mensagem": "Login realizado com sucesso. Buscando novos editais...",
        "usuario": {
            "id": usuario_encontrado['id'],
            "nome": usuario_encontrado['nome'],
            "email": usuario_encontrado['email'],
            "nivel_graduacao": usuario_encontrado['nivel_graduacao']
        }
    }

@app.get("/editais")
def listar_editais():
    editais = edital_dao.listar_todos()
    return editais

@app.post("/editais")
def salvar_edital(edital: EditalInput):
    edital_dict = edital.dict()
    sucesso = edital_dao.salvar(edital_dict)
    if sucesso:
        return {"mensagem": "Edital salvo com sucesso"}
    else:
        return {"mensagem": "Edital não salvo (provavelmente duplicado)"}