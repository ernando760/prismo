# Validação da candidata v0.1.0-alpha.2

Preparação em 2026-11-04, em Linux, com Python 3.14.7, Node 22.14.0 e npm 10.9.2.
Os cenários conversacionais usaram a Skill de desenvolvimento via symlink em
consumidores sintéticos separados; nenhum POC foi modificado.

## Cenários conversacionais exercitados

- `init` apresentou proposta e aguardou aprovação de teste; as cinco fundações
  foram criadas e retomadas. Decisões e tokens permaneceram idênticos em retomada
  concluída. O único par de contraste declarado atingiu 21:1.
- `custom` registrou `base`, `role` e `widget`; spacing e borders foram criados
  com os prefixos aplicáveis. O prefixo de componente não foi exercitado em componente.
- Um projeto sintético sem `decisions.naming` retomou spacing e borders preservando
  decisões, tokens e nomes existentes; isso não cobre todos os formatos legados.
- Um pedido conflitante de alteração da base de spacing provocou esclarecimento
  antes de gravação. A interface de aprovação interativa de comando foi observada
  separadamente da aprovação de design; o pedido de comando de teste foi cancelado.

## Integridade de retomada

A revisão identificou que uma transação de spacing interrompida podia ser ignorada
por um pedido somente de borders, impedindo retomada automática posterior. A correção
verifica journals globalmente antes de executar outra etapa. Regressões cobrem troca
de escopo, retomada prioritária, continuação, edições externas, múltiplos journals e
journal vazio. Testes antigos de conflito, retomada e nomenclatura continuam incluídos.

## Limitações

A execução conversacional não cobre todos os fluxos ou projetos reais. Não foram
validados integralmente inspeção visual, responsividade, fontes, desempenho,
acessibilidade, SDK/dispositivo Flutter nem equivalência entre plataformas. O par de
contraste e os testes sintéticos não comprovam WCAG completa ou distribuição de
pacotes reais. A descoberta automática da Skill em sessão nova não foi comprovada.
As sessões não interativas não comprovam aprovações de comando do Codex.

## Verificações da candidata

- `npm test`: aprovado, com 276 testes Python e 53 testes JavaScript, sem skips.
  Inclui o smoke sintético de distribuição e as regressões de retomada e conflito.
- `npm run test:distribution`: aprovado separadamente (1 teste).
- `bash -n scripts/install.sh`: aprovado; `python3 -m unittest discover -s tests
  -p test_install.py -v`: 14 testes aprovados.
- `quick_validate.py skills/prismo` do skill-creator: `Skill is valid!`.
- `git diff --check`: aprovado para arquivos rastreados modificados. Dependências
  existentes foram usadas; esta execução não comprova uma instalação npm limpa.
