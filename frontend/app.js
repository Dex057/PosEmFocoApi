// Helpers compartilhados pelas páginas. A API é servida na mesma origem
// (as páginas vêm de /frontend/ do próprio FastAPI), por isso os caminhos são absolutos.

const sessao = typeof localStorage !== 'undefined'
    ? JSON.parse(localStorage.getItem('sessao') || 'null')
    : null;

async function api(caminho, opcoes = {}) {
    const headers = { 'Content-Type': 'application/json', ...(opcoes.headers || {}) };
    if (sessao?.token) headers['Authorization'] = `Bearer ${sessao.token}`;

    const resp = await fetch(caminho, { ...opcoes, headers });
    const corpo = await resp.json().catch(() => null);

    if (resp.status === 401) {
        localStorage.removeItem('sessao');
        window.location.href = 'login.html';
        throw new Error('Sessão expirada');
    }
    if (!resp.ok) throw new Error(corpo?.detail || `Erro ${resp.status}`);
    return corpo;
}

function exigirSessao() {
    if (!sessao) window.location.href = 'login.html';
    return sessao;
}

function sair() {
    localStorage.removeItem('sessao');
    window.location.href = 'login.html';
}

let timerToast;
function toast(mensagem, tipo = 'sucesso') {
    let el = document.getElementById('toast');
    if (!el) {
        el = document.createElement('div');
        el.id = 'toast';
        document.body.appendChild(el);
    }
    el.textContent = mensagem;
    el.className = `visivel ${tipo}`;
    clearTimeout(timerToast);
    timerToast = setTimeout(() => { el.className = ''; }, 4000);
}

// Roda uma ação de botão mostrando "carregando" e reabilitando no fim.
async function comBotao(botao, textoCarregando, acao) {
    const original = botao.textContent;
    botao.disabled = true;
    botao.textContent = textoCarregando;
    try {
        return await acao();
    } catch (erro) {
        toast(erro.message, 'erro');
    } finally {
        botao.disabled = false;
        botao.textContent = original;
    }
}

function iniciais(nome) {
    const partes = String(nome || '').trim().split(/\s+/).filter(Boolean);
    if (!partes.length) return '?';
    return (partes[0][0] + (partes.length > 1 ? partes[partes.length - 1][0] : '')).toUpperCase();
}

function paraData(texto) {
    const achado = /(\d{2})\/(\d{2})\/(\d{4})/.exec(texto || '');
    if (!achado) return null;
    const [, dia, mes, ano] = achado;
    const data = new Date(Number(ano), Number(mes) - 1, Number(dia));
    return Number.isNaN(data.getTime()) ? null : data;
}

// O scraper grava o resumo como "[UFPA] Contém: computação" e o motor do SIGAA põe o
// período no título. Aqui isso vira etiqueta de instituição e de prazo.
function interpretarEdital(edital, hoje = new Date()) {
    const resumo = edital.resumo || '';
    const casouResumo = /^\[([^\]]+)\]\s*Contém:\s*(.+)$/i.exec(resumo);

    let titulo = edital.titulo || '(sem título)';
    let prazo = null;

    const casouPrazo = /\s*\(inscrições:\s*([^)]+)\)\s*$/i.exec(titulo);
    if (casouPrazo) {
        titulo = titulo.slice(0, casouPrazo.index).trim();
        const periodo = casouPrazo[1].trim();
        const fim = paraData(periodo.split(/\ba\b/).pop());
        prazo = { rotulo: `inscrições: ${periodo}`, urge: false };

        if (fim) {
            const zerar = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
            const dias = Math.round((zerar(fim) - zerar(hoje)) / 86400000);
            if (dias < 0) prazo = { rotulo: 'inscrições encerradas', urge: false };
            else if (dias === 0) prazo = { rotulo: 'último dia de inscrição', urge: true };
            else prazo = { rotulo: `encerra em ${dias} dia${dias > 1 ? 's' : ''}`, urge: dias <= 7 };
        }
    }

    return {
        titulo,
        prazo,
        instituicao: casouResumo ? casouResumo[1] : null,
        palavra: casouResumo ? casouResumo[2] : (resumo || null),
    };
}

// Links vêm de sites externos: só deixa passar http(s).
function linkSeguro(url) {
    try {
        const base = typeof window !== 'undefined' ? window.location.origin : 'https://x';
        const parsed = new URL(url, base);
        return ['http:', 'https:'].includes(parsed.protocol) ? parsed.href : null;
    } catch {
        return null;
    }
}

if (typeof module !== 'undefined') {
    module.exports = { interpretarEdital, iniciais, linkSeguro, paraData };
}
