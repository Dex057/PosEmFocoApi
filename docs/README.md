# 📖 Documentação Completa - PósEmFoco

Bem-vindo à documentação técnica completa do **PósEmFoco**. Este é o ponto central para entender, desenvolver e manter o projeto.

## 📑 Índice de Documentação

### 🚀 **Começar Aqui**
- [**Instalação Detalhada**](guias/instalacao.md) - Passo a passo completo para cada SO
- [**Configuração**](guias/configuracao.md) - Setup do ambiente e variáveis
- [**Primeiro Uso**](guias/primeiro-uso.md) - Tutorial prático da aplicação
- [**FAQ**](faq.md) - Perguntas frequentes

### 🏗️ **Arquitetura & Design**
- [**Visão Geral da Arquitetura**](arquitetura/visao-geral.md) - Decisões de design e padrões
- [**Modelo de Banco de Dados**](arquitetura/banco-dados.md) - Schema completo, relacionamentos, queries
- [**Fluxo de Autenticação**](arquitetura/fluxo-autenticacao.md) - Como login/registro funciona
- [**Fluxo de Scraping**](arquitetura/fluxo-scraping.md) - Detalhamento do web scraper

### 📡 **API REST**
- [**Introdução à API**](api/introducao.md) - Conceitos e convenções
- [**Autenticação**](api/autenticacao.md) - Como autenticar requisições
- [**Endpoints Completos**](api/endpoints.md) - Documentação técnica de todos os endpoints

### ⚙️ **Componentes Técnicos**
- [**Scraper**](componentes/scraper.md) - Sistema de web scraping
- [**Email Service**](componentes/email-service.md) - Notificações por e-mail
- [**DAO Layer**](componentes/dao-layer.md) - Padrão de acesso a dados
- [**Models**](componentes/models.md) - Estrutura de dados

### 👨‍💻 **Para Desenvolvedores**
- [**Guia de Desenvolvimento**](guias/desenvolvimento.md) - Setup para contribuidores
- [**Padrões de Código**](guias/desenvolvimento.md#padrões-de-código) - Convenções e best practices
- [**Como Contribuir**](guias/desenvolvimento.md#contribuindo)

### 🚀 **Deployment & Produção**
- [**Guia de Deployment**](deployment.md) - Deploy em produção
- [**Monitoramento**](deployment.md#monitoramento) - Logs e observabilidade
- [**Backup e Recovery**](deployment.md#backup-e-recovery) - Estratégia de dados

### 🐛 **Suporte**
- [**Troubleshooting Completo**](troubleshooting.md) - 30+ problemas com soluções
- [**FAQ**](faq.md) - Perguntas frequentes

---

## 🎯 Roteiros por Persona

### 👤 **Usuário Final**
1. Leia: [Primeiro Uso](guias/primeiro-uso.md)
2. Se tiver dúvidas: [FAQ](faq.md)
3. Se tiver erros: [Troubleshooting](troubleshooting.md)

### 👨‍💻 **Desenvolvedor (Setup Local)**
1. Leia: [Instalação](guias/instalacao.md)
2. Leia: [Guia de Desenvolvimento](guias/desenvolvimento.md)
3. Explore: [Arquitetura](arquitetura/visao-geral.md)
4. Consulte: [Componentes](componentes/)

### 🏢 **DevOps / Sysadmin (Produção)**
1. Leia: [Deployment](deployment.md)
2. Leia: [Modelo de Dados](arquitetura/banco-dados.md)
3. Configure: Monitoramento em [Deployment](deployment.md#monitoramento)
4. Backup: [Estratégia](deployment.md#backup-e-recovery)

### 🔍 **Code Reviewer / Auditor**
1. Leia: [Arquitetura](arquitetura/visao-geral.md)
2. Revise: [Componentes](componentes/)
3. Valide: [Padrões de Código](guias/desenvolvimento.md#padrões-de-código)
4. Teste: [API Endpoints](api/endpoints.md)

---

## 📊 Visão Rápida

### Stack Tecnológico
```
Frontend:     HTML5 + CSS3 + JavaScript
Backend:      Python 3.10+ (FastAPI)
Database:     PostgreSQL 12+
Scraping:     Selenium + WebDriver Manager
Auth:         bcrypt + passlib
Email:        SMTP (Gmail)
Deploy:       Uvicorn + systemd/Docker
```

### Estrutura de Pastas
```
PosEmFoco/
├── app/                    # Código principal
│   ├── dao/               # Data Access Objects
│   ├── models/            # Estrutura de dados
│   ├── services/          # Lógica de negócio
│   └── utils/             # Utilitários
├── frontend/              # Interface web
├── docs/                  # Documentação (você está aqui!)
├── server.py              # Servidor FastAPI
└── requirements.txt       # Dependências
```

---

## 🔗 Links Importantes

- 📦 **Repositório:** [GitHub](https://github.com/seu-usuario/PosEmFoco)
- 🐛 **Issues:** [Reportar Bug](https://github.com/seu-usuario/PosEmFoco/issues)
- 📝 **Discussions:** [Conversar](https://github.com/seu-usuario/PosEmFoco/discussions)

---

## 📝 Últimas Atualizações

- **25 de janeiro de 2026** - Documentação completa criada
- **24 de janeiro de 2026** - v1.0.0 Released

---

## ❓ Precisa de Ajuda?

1. **Problema técnico?** → [Troubleshooting](troubleshooting.md)
2. **Dúvida geral?** → [FAQ](faq.md)
3. **Quer contribuir?** → [Guia de Desenvolvimento](guias/desenvolvimento.md)
4. **Deploy em produção?** → [Guia de Deployment](deployment.md)

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
