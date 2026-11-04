# Prismo v0.1.0-alpha.2 — release experimental

Esta release experimental mantém uma Skill e seis operações: `init`, `foundations`,
`tokens`, `create`, `document` e `audit`.

## Mudanças

- `foundations` executa as cinco fundações ou um subconjunto solicitado, com
  checklist persistente, origens das decisões, validação e retomada. Adições com
  decisões fornecidas ou padrões seguros não exigem aprovação por etapa; identidade,
  escolhas essenciais e conflitos ainda exigem esclarecimento.
- Transações interrompidas são verificadas em todo o checklist. Outras etapas não
  avançam antes da recuperação; edições externas conflitantes não são sobrescritas.
- A política opcional de nomes `recommended` ou `custom` é consultada pelas seis
  operações. Projetos sem `decisions.naming` preservam os nomes e o comportamento
  anteriores; não há migração automática. Consulte o [guia](https://github.com/ernando760/prismo/blob/v0.1.0-alpha.2/skills/prismo/references/naming.md).

## Escopo de validação e limites

Sessões novas do Codex exercitaram `init`, criação e retomada das cinco fundações,
`custom` com spacing e borders, retomada legada sem `decisions.naming` e um conflito
de design em consumidores sintéticos. A interface interativa de aprovação de
comandos foi verificada separadamente da aprovação de design da Skill. Nem todos
os fluxos, prefixos de componentes ou projetos reais foram exercitados
conversacionalmente; a seleção automática da Skill não foi comprovada.

DTCG, auditoria e busca de impacto têm cobertura parcial. Cálculos de contraste,
DOM simulado e testes de distribuição sintética não comprovam WCAG completa,
inspeção visual, responsividade, desempenho ou funcionamento de pacotes reais.
Flutter/Widgetbook em SDK e dispositivo, outros sistemas operacionais e equivalência
visual entre plataformas não foram validados integralmente. A execução de foundations
usa lock local, que não coordena editores externos; não edite os mesmos arquivos
durante a execução. Preservam-se os demais [limites experimentais](https://github.com/ernando760/prismo/blob/v0.1.0-alpha.2/README.md#limites-de-uso-experimental).

Os resultados e seu escopo estão no [registro de validação](https://github.com/ernando760/prismo/blob/v0.1.0-alpha.2/docs/evidencias-alpha2/RESULTADOS.md).
As notas e resultados da alpha.1 permanecem como histórico. Esta release não garante
prontidão para produção.
