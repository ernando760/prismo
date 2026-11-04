# Estabilização após POC 2

Escopo: alterações somente no Prismo; seis operações preservadas, sem mudanças no
POC, novas dependências ou refatorações visuais. Cada etapa é validada antes da próxima.

- [x] 1. `create`: orientar validação do tarball e consumo público (exports,
  declarações TypeScript, CSS, NodeNext/Bundler conforme suporte); revisão de plano
  compatível com entradas existentes, sem confundir comandos planejados com executados.
- [x] 2. Elevation: aliases semânticos hierárquicos e regressões de compatibilidade,
  colisões, nomes inválidos, projeções e preservação das entradas.
- [x] 3. `audit`: ignorar artefatos gerados comuns, aceitar exclusões explícitas e
  informar cobertura; manter leitura de fontes DTCG declaradas e operação somente leitura.
- [x] 4. Avaliar módulos de apresentação Docusaurus/Storybook; mudar apenas se
  houver solução simples, segura e compatível com instalações existentes.
- [x] 5. Executar suíte completa e validar estrutura, referências e distribuição da Skill.

Resultados e limitações registrados abaixo; todas as etapas concluídas.

Etapa 1: 32 testes create aprovados. Smoke isolado com npm pack/install offline,
Node, TypeScript 5.9.3 (NodeNext e Bundler, skipLibCheck false) e esbuild 0.28.2
aprovado; detectou extensão ESM ausente, declarações ausentes, CSS ausente e export
quebrado. Sem instalação de ferramentas; dependências existentes lidas, sem escrita
no POC. Comandos do plano nunca executados pelo helper.

Etapa 2: 22 testes Elevation aprovados. Mapas legados, pontuados e aninhados
produzem aliases DTCG compatíveis; projeções permanecem equivalentes. Nomes
inválidos, caminhos normalizados repetidos e colisões token/grupo recusados;
reexecução e preservação das entradas verificadas.

Etapa 3: 29 testes audit aprovados, incluindo CLI somente leitura, exclusões
aninhadas, fronteiras de caminhos, symlinks/traversal recusados, limite após filtros,
evidências excluídas manuais e validação DTCG preservada. Exclusões são caminhos
literais, não globs; filtros e cobertura estão descritos na referência.

Etapa 4: avaliada sem refatoração. DocumentUI.jsx importa os mesmos catalog.mjs
e dtcg.mjs usados pelos adaptadores Storybook. A orientação document-visual.md já
manda reutilizar módulos existentes, ajustar imports e registrar origem/atualização.
Cópias locais em aplicações independentes podem divergir, mas centralizá-las por
pacote/workspace ou mudar caminhos automaticamente exigiria configuração dos
builders e migração de consumidores. Não há correção genérica simples e segura;
assets e imports existentes foram preservados. Os testes de renderização/SSR e
adaptadores na suíte final exercitam o compartilhamento atual.

## Validação final

- `python3 -m unittest discover -s tests -p 'test_create*.py' -q`: 32 aprovados.
- `python3 -m unittest discover -s tests -p test_elevation.py -q`: 22 aprovados.
- `python3 -m unittest discover -s tests -p test_audit.py -q`: 29 aprovados.
- `npm test`: 234 Python + 53 JavaScript aprovados, zero falhas, skips ou cancelados.
  Inclui instalador, integração entre operações, JSON estrito, catálogo DOM,
  adaptadores HTML/React, MDX e SSR. Log: `/tmp/prismo-poc2-suite-compatible.log`.
- `python3 /tmp/prismo-distribution-check.py`: smoke positivo/negativo de pacote
  descrito na etapa 1; npm pack e instalação offline do tarball em diretório temporário,
  import runtime pelo nome público, tsc em ambos os modos e bundle real do CSS.
- `python3 /home/ernandomfr/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/prismo`:
  `Skill is valid!`.
- `bash -n scripts/install.sh`: aprovado. Referências Markdown locais conferidas;
  seis operações e restrição de múltiplos agentes preservadas.

Para reproduzir a suíte com as instalações compatíveis já disponíveis nesta máquina:

```bash
PRISMO_JSDOM_PATH=/home/ernandomfr/Documentos/Projects/prismo-poc/node_modules/jsdom \
PRISMO_STORYBOOK_TEST_PACKAGE=/home/ernandomfr/Documentos/Projects/prismo-poc/package.json \
PRISMO_DOCUMENT_TEST_PACKAGE=/home/ernandomfr/Documentos/Projects/prismo-poc/package.json \
npm test
```

## Limites

A primeira tentativa usou jsdom 30 do ambiente POC 2 e falhou na parte DOM por
incompatibilidade com Node 22.14.0; o runner recusou os resultados incompletos.
A repetição usou jsdom 26.1.0 já instalado, compatível com o manifesto do Prismo,
em leitura; nenhum pacote foi instalado no Prismo ou nos POCs. O smoke de distribuição
usou TypeScript/esbuild existentes e uma fixture sintética, não validou nem modificou
o pacote do POC. Scripts, tarballs e consumidores do smoke ficaram em `/tmp`.

O helper create revisa cobertura declarada, não executa nem certifica checks;
`distribution` é opcional para preservar planos anteriores. O fluxo da Skill exige
investigar bibliotecas e validar a distribuição quando aplicável. Não há detecção
universal de bibliotecas ou de arquivos gerados; exclusões adicionais do audit são
caminhos literais explícitos. Aliases Elevation para outros semânticos preservam a
regra anterior de alvo existente ou já emitido; não foi adicionado ordenamento de
referências futuras. A duplicação física entre aplicações continua possível,
conforme avaliação da etapa 4. Não houve refatoração visual, publicação ou avaliação
interativa de uma nova sessão de seleção automática da Skill.


## Continuidade da preparação

A contagem e o smoke em `/tmp` acima são evidências da execução original. A
incorporação do smoke à suíte, o lockfile e a tentativa de instalação limpa são
acompanhados no [checklist da release experimental](experimental-release-checklist.md).
