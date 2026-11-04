# Prismo v0.1.0-alpha.1 — release experimental

Versão experimental para uso acompanhado, com as limitações descritas abaixo.
Preparada para publicação no GitHub como pre-release. A arquitetura continua com uma única Skill,
seis operações e referências sob demanda; nenhum POC foi modificado.

## Disponível

As operações `init`, `foundations`, `tokens`, `create`, `document` e `audit` estão
implementadas nos escopos da [tabela de operações](../README.md#operações-disponíveis).
As cinco fundações têm helpers determinísticos e prévias DTCG. `create` e `document`
são fluxos guiados com revisão/inventário; os helpers não substituem implementação,
execução de testes ou aprovação do usuário. `audit` permanece somente leitura.

A estabilização inclui aliases semânticos hierárquicos de Elevation, escopo/exclusões
do audit e orientação de distribuição Web com exports, tipos, CSS e resoluções
NodeNext/Bundler. Planos legados continuam aceitos. Instalação local por cópia ou
symlink, atualização de instalações reconhecidas e backups estão disponíveis.

Esta preparação acrescenta documentação consolidada, dependências de teste fixadas,
lockfile npm e smoke obrigatório versionado de distribuição. O smoke usa tarball e
consumidor sintéticos e verifica também falhas controladas; não publica nem certifica
pacotes de consumidores. Não foram adicionadas funcionalidades às operações.

## Requisitos e compatibilidade

Consulte os [requisitos e instalação](../README.md#instalação-local) e o
[contrato de caminhos](../skills/prismo/references/project-path-contract.md).
Linux é o ambiente testado; macOS/Windows não foram validados. A instalação da
Skill não instala ferramentas de catálogo, portal, SDK ou dependências de testes.

A atualização substitui toda a instalação reconhecida e preserva backup; não mescla
customizações. Symlink exige manter a origem no mesmo caminho e seu backup não
preserva o conteúdo histórico. Não há migração automática de projetos ou tokens.

## Recursos e cenários ainda não comprovados integralmente

- Descoberta automática em sessão nova e execução conversacional completa dos
  fluxos, incluindo qualidade de decisões, implementação e inspeção no consumidor.
- Componentes Flutter/Widgetbook gerados, compilados e exercitados em SDK/device.
- Inspeção visual, responsividade, desempenho e acessibilidade em browser/leitor
  de tela. Testes DOM/SSR e cálculos não comprovam conformidade WCAG completa.

## Restrições conhecidas

DTCG é parcial; audit e busca de impacto são textuais e limitados. Os formatos,
limites e caminhos de referência estão consolidados nas
[limitações de uso](../README.md#limites-de-uso-experimental). Distribuição exige
validação de cada pacote real. Não há garantia geral para outros renderers,
frameworks, plataformas ou projetos. Cópias de módulos de apresentação entre
aplicações podem divergir. Marketing não possui gerador de componentes próprio.

## Evidências e liberação

Comandos, contagens e bloqueios desta preparação estão no
[checklist de preparação](experimental-release-checklist.md). Resultados antigos
foram preservados como histórico e não representam automaticamente o estado atual.

A verificação complementar de 2026-11-04 aprovou `npm ci` padrão com lifecycle e
a suíte usando essa instalação, em sandbox Linux com rede e subprocessos permitidos.
O runner passou a selecionar TAP explicitamente para compatibilidade com Node 24;
falhas e skips continuam sendo recusados. O bloqueio técnico de instalação foi
encerrado; as lacunas acima delimitam o uso experimental e devem acompanhar a release.
A publicação desta versão deve usar a tag anotada `v0.1.0-alpha.1` e o indicador
pre-release do GitHub.
