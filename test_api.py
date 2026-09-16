"""Checagem rápida da API com DAOs falsos (sem banco).

Rodar os testes:  python test_api.py
Ver o front sem Postgres: python test_api.py --servir
"""
import logging
import sys

from fastapi.testclient import TestClient

import server

# Barulho de fora do que está sendo testado: uma linha por requisição (httpx) e o aviso
# do passlib ao ler a versão do bcrypt (cosmético, o hash funciona).
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("passlib").setLevel(logging.ERROR)


class UsuarioDAOFalso:
    def __init__(self):
        self.usuarios = {}

    def salvar(self, usuario):
        usuario_id = len(self.usuarios) + 1
        self.usuarios[usuario.email] = {
            "id": usuario_id,
            "nome": usuario.nome,
            "email": usuario.email,
            "senha_hash": usuario.senha_hash,
            "nivel_graduacao": usuario.nivel_graduacao,
        }
        return usuario_id

    def buscar_por_email(self, email):
        return self.usuarios.get(email)


class InteresseDAOFalso:
    def __init__(self):
        self.por_usuario = {}

    def substituir(self, usuario_id, lista):
        self.por_usuario[usuario_id] = [p.strip() for p in lista if p.strip()]
        return True

    def listar_por_usuario(self, usuario_id):
        return self.por_usuario.get(usuario_id, [])


class EditalDAOFalso:
    editais = [
        {"id": 1, "titulo": "Mestrado em Computação", "link": "https://u.br/1", "resumo": None},
        {"id": 2, "titulo": "Doutorado em Direito", "link": "https://u.br/2", "resumo": None},
    ]

    def listar_todos(self):
        return self.editais

    def listar_por_palavras(self, palavras):
        return [e for e in self.editais if any(p.lower() in e["titulo"].lower() for p in palavras)]


def usar_daos_falsos():
    server.usuario_dao = UsuarioDAOFalso()
    server.interesse_dao = InteresseDAOFalso()
    server.edital_dao = EditalDAOFalso()


def demo():
    usar_daos_falsos()

    disparos = []
    server.executar_scraper = lambda: disparos.append(1)

    cliente = TestClient(server.app)

    novo = {"nome": "Ana", "email": "ana@x.br", "senha": "senha123",
            "nivel_graduacao": "mestrado", "interesses": ["computação"]}

    curta = cliente.post("/cadastro", json={**novo, "senha": "123"})
    assert curta.status_code == 400, f"senha curta devia falhar, veio {curta.status_code}"

    assert cliente.post("/cadastro", json=novo).status_code == 200
    assert cliente.post("/cadastro", json=novo).status_code == 400, "e-mail duplicado devia falhar"

    errada = cliente.post("/login", json={"email": "ana@x.br", "senha": "outra"})
    assert errada.status_code == 401, "senha errada devia dar 401"

    login = cliente.post("/login", json={"email": "ana@x.br", "senha": "senha123"})
    assert login.status_code == 200, login.text
    auth = {"Authorization": f"Bearer {login.json()['token']}"}

    assert cliente.get("/me/interesses").status_code == 401, "sem token devia dar 401"
    assert cliente.get("/me/interesses", headers={"Authorization": "Bearer inventado"}).status_code == 401

    assert cliente.get("/me/interesses", headers=auth).json() == ["computação"]

    salvou = cliente.put("/me/interesses", json={"interesses": ["direito", "  ", " ia "]}, headers=auth)
    assert salvou.json() == ["direito", "ia"], salvou.json()

    meus = cliente.get("/me/editais", headers=auth).json()
    assert [e["id"] for e in meus] == [2], f"devia casar só o de direito, veio {meus}"

    assert len(cliente.get("/editais").json()) == 2

    assert cliente.post("/scraper/rodar", headers=auth).status_code == 200
    assert disparos == [1], "o scraper devia ter sido disparado uma vez"

    assert cliente.get("/", follow_redirects=False).headers["location"] == "/frontend/login.html"

    print("OK: cadastro, login, sessão, interesses, filtro de editais e disparo do scraper.")


def servir():
    """Sobe a API com dados falsos, só para conferir o front sem Postgres."""
    import uvicorn

    usar_daos_falsos()
    # Amostra no formato que o scraper realmente grava, para o front mostrar as
    # etiquetas de instituição e de prazo como mostraria em produção.
    server.edital_dao.editais = [
        {"id": 1, "titulo": "MESTRADO EM CIÊNCIA DA COMPUTAÇÃO - PPGCC EDITAL 02/2026 (inscrições: 10/09/2026 a 19/09/2026)",
         "link": "https://sigaa.ufpa.br/sigaa/public/programa/portal.jsf?id=1#ps1", "resumo": "[UFPA] Contém: computação"},
        {"id": 2, "titulo": "DOUTORADO EM RECURSOS NATURAIS DA AMAZÔNIA (inscrições: 01/10/2026 a 30/11/2026)",
         "link": "https://sigaa.ufopa.edu.br/sigaa/public/programa/portal.jsf?id=2#ps2", "resumo": "[UFOPA] Contém: amazônia"},
        {"id": 3, "titulo": "PROCESSO SELETIVO PARA O CURSO DE PÓS-GRADUAÇÃO LATO SENSU EM ENFERMAGEM DO TRABALHO",
         "link": "https://sistemas.uepa.br/sgps/selecao/#enfermagem", "resumo": "[UEPA] Contém: enfermagem"},
        {"id": 4, "titulo": "Ufra abre processo seletivo de professor bolsista para especialização",
         "link": "https://novo.ufra.edu.br/noticia-4", "resumo": "[UFRA] Contém: especialização"},
    ]
    server.executar_scraper = lambda: print("Modo demo: scraper não roda de verdade.")

    TestClient(server.app).post("/cadastro", json={
        "nome": "Usuária Demo", "email": "demo@posemfoco.br", "senha": "demo123",
        "nivel_graduacao": "mestrado", "interesses": ["computação"],
    })

    print("Front: http://127.0.0.1:8000/frontend/login.html  (demo@posemfoco.br / demo123)")
    uvicorn.run(server.app, host="127.0.0.1", port=8000, log_level="warning")


if __name__ == "__main__":
    servir() if "--servir" in sys.argv else demo()
