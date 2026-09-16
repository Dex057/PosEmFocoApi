// Checagem das funções puras do front. Rodar: node frontend/test_app.js
const assert = require('assert');
const { interpretarEdital, iniciais, linkSeguro } = require('./app.js');

const HOJE = new Date(2026, 8, 16); // 16/09/2026

// Item vindo do motor do SIGAA: instituição no resumo, período no título.
let item = interpretarEdital({
    titulo: 'MESTRADO EM SOCIOLOGIA - PPGSA (inscrições: 15/09/2026 a 20/09/2026)',
    resumo: '[UFPA] Contém: sociologia',
}, HOJE);

assert.strictEqual(item.titulo, 'MESTRADO EM SOCIOLOGIA - PPGSA', 'o prazo sai do título');
assert.strictEqual(item.instituicao, 'UFPA');
assert.strictEqual(item.palavra, 'sociologia');
assert.deepStrictEqual(item.prazo, { rotulo: 'encerra em 4 dias', urge: true });

// Prazo distante não é urgente; prazo vencido e último dia têm rótulo próprio.
const prazoDe = (periodo) => interpretarEdital(
    { titulo: `X (inscrições: ${periodo})`, resumo: '' }, HOJE).prazo;

assert.deepStrictEqual(prazoDe('01/10/2026 a 30/11/2026'), { rotulo: 'encerra em 75 dias', urge: false });
assert.deepStrictEqual(prazoDe('01/08/2026 a 30/08/2026'), { rotulo: 'inscrições encerradas', urge: false });
assert.deepStrictEqual(prazoDe('01/09/2026 a 16/09/2026'), { rotulo: 'último dia de inscrição', urge: true });
assert.strictEqual(prazoDe('a combinar').rotulo, 'inscrições: a combinar', 'sem data, mostra o texto cru');

// Item de portal comum: sem período, sem instituição no formato esperado.
item = interpretarEdital({ titulo: 'Ufra abre processo seletivo', resumo: '' });
assert.strictEqual(item.prazo, null);
assert.strictEqual(item.instituicao, null);
assert.strictEqual(item.titulo, 'Ufra abre processo seletivo');

assert.strictEqual(iniciais('Edson Davi Martins'), 'EM');
assert.strictEqual(iniciais('Ana'), 'A');
assert.strictEqual(iniciais(''), '?');

assert.strictEqual(linkSeguro('javascript:alert(1)'), null, 'link de script não passa');
assert.ok(linkSeguro('https://ufpa.br/edital'));

console.log('OK: etiqueta de instituição, prazo com urgência, iniciais e link seguro.');
