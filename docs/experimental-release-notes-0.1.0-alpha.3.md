# Prismo v0.1.0-alpha.3 — candidata experimental

Preparada localmente, sem tag ou GitHub Release. Mantém uma Skill, as seis
operações (`init`, `foundations`, `tokens`, `create`, `document`, `audit`) e a
arquitetura existente. Esta candidata não garante prontidão para produção.

## Mudanças de Colors

- Granularidade orientada por cobertura funcional e evolução fundamentada, sem
  quantidade fixa de tons ou geração especulativa de escalas.
- Matriz incremental dos usos afetados por tema, distinguindo cobertura concluída,
  parcial, adiada e não avaliada; reuso → extensão → exceção justificada.
- Cores específicas de componentes continuam permitidas. Novos aliases exigem
  intenção útil; igualdade de valores não obriga consolidação.
- `colors.py palette --require-coverage` valida a matriz antes de propostas novas;
  `--plan -` aceita stdin, e `palette --help` explica o contrato JSON e os valores
  válidos. Retorno e stderr devem ser conferidos antes de interpretar stdout.
- Relatórios perceptuais sobre sRGB final, rastreabilidade de aliases e resumos
  padrão, com detalhes via `--full`. Medidas não garantem harmonia visual.

O [guia de cobertura](../skills/prismo/references/colors-coverage.md) integra esse
fluxo às operações existentes. Consulta legada ou contraste pontual não exige
reconstruir a matriz. O preview incremental não substitui o histórico persistido.

## Compatibilidade e persistência

Planos sem `coverage` continuam aceitos no modo legado e recebem cobertura
desconhecida. Não há migração automática, renumeração de tokens aprovados ou
promoção automática das exceções de componente. Migrações exigem aprovação.

A cobertura participa dos registros existentes de foundations, com journal,
lock, proteção contra conflitos e retomada. Conclusão técnica não significa
inspeção visual integral. `audit` continua somente leitura; as regras de aprovação
de create/tokens e a autorização aditiva de foundations são preservadas.

## Validação e limitações

A [evidência durável da candidata](evidencias-alpha3/RESULTADOS.md) registra a suíte,
a integração anterior no Nexa DS e dois planos efetivamente validados em sessões
novas do Codex. As falhas conversacionais iniciais foram corrigidas nos dois casos
reavaliados, sem estabelecer confiabilidade universal.

- Cálculo, visual declarado e conformidade são evidências distintas. O helper não
  confirma a veracidade de capturas, justificativas ou decisões contextuais.
- Link e seleção propostos não foram implementados ou aprovados visualmente;
  combinações de estados e harmonia nos novos contextos continuam pendentes.
- Ainda houve leitura excessiva de decisões e repetição de referências nas
  sessões observadas; o consumo de contexto não está integralmente resolvido.
- Preservam-se DTCG parcial, limites sRGB/composição, busca textual e necessidade
  de revisão de fontes divididas/contextos alternativos. Não se afirma WCAG completa.
- Flutter/dispositivo, outros sistemas operacionais, descoberta automática da
  Skill e todos os fluxos em consumidores reais não foram validados integralmente.

Os demais [limites experimentais](../README.md#limites-de-uso-experimental) continuam
aplicáveis. Notas e evidências das releases anteriores permanecem como histórico.

Publicação futura exige os controles de [AGENTS.md](../AGENTS.md), tag anotada
inédita e indicador de pre-release. Nenhuma publicação é realizada por estas notas.
