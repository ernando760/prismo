# Preparação da primeira release experimental

Escopo aprovado: documentação, histórico de validação, testes de distribuição e
reprodução das dependências de desenvolvimento. Sem novas operações, alterações
de versão, publicação ou mudanças nos POCs. Etapas executadas em ordem; conclusão
é registrada somente após a validação correspondente.

- [x] 1. Atualizar README e referências de uso para as seis operações atuais;
  conferir links e distinguir operação guiada de validação determinística.
- [x] 2. Corrigir pendências históricas já superadas, preservando resultados e
  bloqueios originais com ligação para as evidências posteriores.
- [x] 3. Versionar e integrar o smoke de distribuição à suíte: tarball, exports,
  declarações TypeScript, CSS, NodeNext/Bundler e falhas controladas.
- [x] 4. Declarar dependências de teste, gerar lockfile e tentar instalação limpa;
  registrar qualquer bloqueio sem contar como aprovação.
- [x] 5. Consolidar requisitos, instalação, atualização e limitações conhecidas.
- [x] 6. Preparar notas da release experimental com capacidades, restrições e
  validações pendentes, sem definir ou alterar versão.
- [x] 7. Validação final: suíte completa, validador da Skill, instalador e smoke
  de distribuição; conferir referências e preservação das seis operações.

- [x] 8. Concluir instalação padrão com lifecycle em ambiente com rede e
  subprocessos permitidos; repetir a suíte e preservar evidências duráveis.

## Evidências por etapa

### 1. Estado das operações

README consolidado com as seis operações e links para os contratos canônicos;
removidos status de fases anteriores e descrições de pastas vazias criadas no init.
Requisito dos helpers uniformizado nas referências para Python 3.9+.
Validação: 6 testes de orientação create aprovados; 39 links locais do README,
roteador e referências conferidos. Operações e scripts de produto preservados.


### 2. Histórico de validação

Checklist arquitetural concluído com ligação para a execução posterior que
superou os skips. Resultados históricos de create/document/audit/Storybook foram
identificados como históricos, sem apagar contagens, bloqueios ou pendências reais.
A etapa POC 2 aponta para esta preparação. Conferidos links locais e pendências:
nenhuma validação concluída permanece marcada como aberta nos checklists antigos.


### 3. Smoke obrigatório versionado

`tests/test_distribution.py` agora é descoberto pelo runner Python de `npm test`;
`npm run test:distribution` permite executá-lo isoladamente. TypeScript 5.9.3 foi
declarado como dependência de desenvolvimento necessária ao teste.
Validação inicial: 1 teste com subcasos positivos e cinco regressões negativas
aprovado (tarball real instalado offline; runtime/exports raiz e subpath, tipos
NodeNext/Bundler, CSS emitido; extensão ESM ausente, declaração ausente, CSS ausente,
subpath CSS não exportado e export JS quebrado). Ferramentas existentes foram
reutilizadas em leitura via `PRISMO_DISTRIBUTION_TEST_PACKAGE`; nenhuma escrita no
POC. O teste não ignora ausência de ferramentas e cria somente temporários.


### 4. Dependências e instalação limpa

Seis dependências de desenvolvimento fixadas em package.json; TypeScript é a única
adição, necessária ao smoke. Node >=22.14.0/npm >=10 declarados. Lockfile v3 gerado
pelo npm 10.9.2 offline a partir de lock compatível existente, recalculado e podado
para este manifesto: 223 entradas com URL do registro e integridade, sem links,
workspaces ou caminhos dos POCs; todas de desenvolvimento. Nenhuma versão do Prismo
foi introduzida ou alterada.

Tentativas isoladas:

- Geração online do lock: falhou com EAI_AGAIN para registry.npmjs.org.
- `npm ci --offline` com cache vazio: falhou com ENOTCACHED.
- Cache isolado abastecido com 198 tarballs disponíveis no cache local, copiados
  em leitura e verificados por integridade do lock (25 binários opcionais de outras
  plataformas ausentes). `npm ci --offline` padrão: falhou no lifecycle do esbuild,
  `spawnSync ... EPERM`, restrição deste ambiente.
- `npm ci --offline --ignore-scripts`: extração limpa de 198 pacotes aprovada.
  Smoke executado com essas ferramentas passou; não houve symlink nem cópia de
  node_modules de outro projeto. Isso não aprova instalação padrão com lifecycle.

Logs em /tmp/prismo-release-lock.log, prismo-release-lock-offline.log,
prismo-release-ci-empty.log, prismo-release-ci-cached.log,
prismo-release-ci-no-lifecycle.log e prismo-release-smoke-clean.log.
Pendência naquela execução: repetir `npm ci` padrão; resolvida na etapa 8 abaixo.


### 5. Ambiente e restrições

README é a referência de instalação/atualização, requisitos de uso e teste e
limitações conhecidas. Conferidos comandos, proteção por marcador/backups, lock
residual e comportamento de symlink contra o instalador. Separados requisitos do
consumidor, dependências de desenvolvimento e verificação adicional Docusaurus.
Documentados os bloqueios de instalação, mínimo Python não exercitado, uso guiado,
DTCG parcial, audit textual, smoke sintético e lacunas Flutter/browser. Links
locais do README/roteador/referências aprovados.


### 6. Notas preparatórias

`docs/experimental-release-notes.md` distingue capacidades disponíveis, cenários
não comprovados, restrições e a condição de instalação então pendente. Requisitos
operacionais permanecem canônicos no README e contratos nas referências da Skill.
Conferidos links, seis operações e ausência de versão/tag ou afirmação de publicação.


### 7. Validação inicial da preparação

Ambiente: Linux, Python 3.14.7, Node 22.14.0 e npm 10.9.2. Dependências obtidas pela
extração limpa offline do lock com `--ignore-scripts`, em
`/tmp/prismo-clean-install-31_sslbj`; sem reutilizar node_modules dos POCs.

| Verificação | Resultado |
| --- | --- |
| `npm test` | 235 testes Python e 53 JavaScript aprovados; zero falhas, skips ou cancelados |
| `npm run test:distribution` | 1 smoke com subcasos positivos e cinco regressões negativas aprovado também isoladamente |
| `python3 -m unittest discover -s tests -p test_install.py -v` | 14 testes aprovados, além da execução na suíte completa |
| `bash -n scripts/install.sh` | aprovado |
| `quick_validate.py skills/prismo` da skill-creator | Skill is valid! |
| Referências e estrutura | 58 links/anchors locais, sintaxe Python e seis operações conferidos |
| Manifesto/lock | seis dependências exatas, integridade/URLs de registro, sem links locais ou versão de produto introduzida |
| `npm ci` padrão | bloqueado naquela execução; encerramento na etapa 8 |

Comandos da suíte usando exclusivamente a árvore extraída nesta preparação:

```bash
PRISMO_JSDOM_PATH=/tmp/prismo-clean-install-31_sslbj/node_modules/jsdom \
PRISMO_STORYBOOK_TEST_PACKAGE=/tmp/prismo-clean-install-31_sslbj/package.json \
PRISMO_DOCUMENT_TEST_PACKAGE=/tmp/prismo-clean-install-31_sslbj/package.json \
PRISMO_DISTRIBUTION_TEST_PACKAGE=/tmp/prismo-clean-install-31_sslbj/package.json \
PYTHONDONTWRITEBYTECODE=1 npm test

PRISMO_DISTRIBUTION_TEST_PACKAGE=/tmp/prismo-clean-install-31_sslbj/package.json \
PYTHONDONTWRITEBYTECODE=1 npm run test:distribution

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_install.py -v
bash -n scripts/install.sh
python3 /caminho/skill-creator/scripts/quick_validate.py skills/prismo
```

Logs: `/tmp/prismo-release-preparation-suite.log`,
`/tmp/prismo-release-installer.log`, `/tmp/prismo-release-distribution-final.log`.
Os caminhos temporários são evidências desta execução; em ambiente normal use
`npm ci && npm test` na raiz, sem as variáveis de reutilização.

### 8. Verificação padrão concluída — 2026-11-04

**Resultado: apto para publicação experimental, dentro dos limites documentados;
sem bloqueadores técnicos restantes identificados nesta verificação.** Nenhuma
versão, tag ou publicação foi criada.

Ambiente: sandbox Vercel temporário e não persistente, Linux x86_64, Node 24.22.1,
npm 11.19.1, Python 3.14.4. A execução partiu sem node_modules e sem cache npm,
com acesso a https://registry.npmjs.org/, `ignore-scripts=false` e sem variáveis
PRISMO_* de reutilização. Não foram copiados node_modules ou caches dos POCs.

| Verificação | Resultado |
| --- | --- |
| `npm ci --foreground-scripts --cache /vercel/sandbox/npm-cache` | exit 0; 198 pacotes instalados; lifecycle habilitado; auditoria npm de 199 pacotes sem vulnerabilidades reportadas |
| esbuild 0.28.2 | postinstall `node install.js` executado sem erro; transformação síncrona e spawnSync do Node aprovados |
| `npm test` | exit 0; 236 Python e 53 JavaScript aprovados; zero skips/cancelamentos/falhas |
| `npm run test:distribution` | exit 0; smoke aprovado também isoladamente, incluindo variantes negativas |
| `python3 -m unittest discover -s tests -p test_install.py -v` | 14 testes aprovados |
| `bash -n scripts/install.sh` | exit 0 |
| `quick_validate.py skills/prismo` | Skill is valid!; PyYAML instalado em venv separado do projeto |
| Regressões do runner | 3 testes aprovados em Node 24 remoto e Node 22.14.0 local; aprovação, falha e skip reais preservam a classificação esperada |
| Manifesto/lock e fontes validadas | SHA-256 antes/depois idênticos; nenhuma versão ou dependência alterada |

#### Diagnóstico e correção necessária

As falhas DNS/EAI_AGAIN e spawnSync/EPERM anteriores pertenciam ao ambiente local:
um subprocesso mínimo independente do Prismo também falhava. O sandbox remoto
permitiu instalar e executar o esbuild normalmente, sem `--ignore-scripts`, patches
do Node ou supressão de lifecycle.

A primeira tentativa no Node 24 expôs um problema real do runner do Prismo: ele
esperava o relatório TAP, enquanto o Node emitia spec por padrão. Os testes JS
passavam, mas eram classificados como incompletos. `scripts/test_suite.py` agora
seleciona `--test-reporter=tap` explicitamente. A regressão nova executa casos reais
de aprovação, falha e skip e confirma que o runner continua recusando falhas/skips.
Não foram alteradas funcionalidades das seis operações. Veja a
[documentação dos reporters Node](https://nodejs.org/docs/latest-v24.x/api/test.html#test-reporters).

A execução foi interrompida pelo usuário antes de preservar o resultado anterior.
O primeiro sandbox encerrou pelo timeout de 10 minutos (status stopped confirmado
na retomada); seus resultados finais não foram contabilizados. Esta etapa repetiu
a cadeia completa em um sandbox novo e salvou os registros antes do encerramento.

#### Evidências e reprodução

O [relatório JSON versionado](evidence/experimental-release-validation-2026-11-04.json)
contém comandos, exit codes, durações, stdout/stderr e hashes antes/depois.
SHA-256 do relatório: `48f3e4e70173443cc80acd4c7de28ff8fa71bae830712024d150e40afea36d00`.
A sessão `sbx_kB0IE57vDLSvdh1cGBdzDVQIa6Hw` foi encerrada após exportar as evidências;
status stopped confirmado. Nenhum servidor, snapshot persistente ou deploy foi criado.

Em uma cópia limpa, execute:

```bash
npm ci --foreground-scripts --cache /caminho/temporario/cache-vazio
npm test
npm run test:distribution
python3 -m unittest discover -s tests -p test_install.py -v
bash -n scripts/install.sh
python3 /caminho/skill-creator/scripts/quick_validate.py skills/prismo
```

O validador externo precisa de PyYAML; na verificação foi usado venv dedicado.
O npm emitiu avisos de depreciação de whatwg-encoding e de allowScripts do esbuild;
o postinstall executou e terminou com sucesso. Nenhum aviso foi ocultado nem levou
a upgrade incidental. Os logs completos estão no relatório.

## Limites para a publicação experimental

A pendência de instalação padrão e execução da suíte com essa árvore foi resolvida.
Permanecem os limites de uso experimental (DTCG parcial, audit textual, smoke
sintético e Flutter/browser/conversação não comprovados integralmente), consolidados
no [README](../README.md#limites-de-uso-experimental) e nas
[notas preparatórias](experimental-release-notes.md). Eles devem acompanhar a release.
Publicar e definir versão/tag continuam fora desta etapa.


## Preparação do primeiro versionamento — v0.1.0-alpha.1

O projeto não possuía histórico Git. O repositório local foi inicializado em main;
o primeiro commit registra uma única baseline estabilizada, sem simular etapas
anteriores. A política de Conventional Commits está no AGENTS.md: título e corpo
em inglês, explicação do que mudou e por quê, autoria Git do usuário preservada e
trailer obrigatório de coautoria válida e autorizada.

A identidade de coautoria foi verificada no próprio Codex instalado:
`Codex <noreply@openai.com>`. Foi autorizada pelo usuário ao identificar a IA
responsável pelo commit e registrada apenas na configuração Git local.

Metadados da release em package.json, package-lock.json e metadata.version da Skill:
`0.1.0-alpha.1`. O formato de decisões `prismo_version: 1` permanece inalterado.
As seis operações e as limitações experimentais foram preservadas.

Validação da candidata: instalação limpa local com npm ci e lifecycle do esbuild,
236 testes Python, 53 JavaScript, zero ignorados, smoke isolado, 14 testes do
instalador, bash -n e validador da Skill aprovados. O
[relatório da candidata](evidence/release-candidate-0.1.0-alpha.1.json) preserva logs
e hashes dos metadados. A única normalização na fixture foi remover uma linha
vazia excedente no EOF para aprovar git diff --check; sem alteração de conteúdo.

A revisão inicial não encontrou padrões de credenciais nos arquivos selecionados.
.gitignore exclui dependências, caches, configurações locais, .env e saídas
temporárias. A criação de remoto público e a publicação dependem da aprovação do
destino concreto pelo usuário; esta evidência não declara publicação realizada.
