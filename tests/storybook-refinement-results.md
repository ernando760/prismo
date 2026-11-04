# Refinamentos das fundações no Storybook

## Alterações compartilhadas

O renderer e o mapeamento em `skills/prismo/assets/storybook/` foram refinados,
preservando a API e o estilo visual anterior. Os templates HTML e React continuam
usando o mesmo renderer.

- **Colors:** as paletas primitivas ficam em área única, fora dos painéis de tema.
  Claro/escuro comparam os semânticos; o filtro também atua na área compartilhada.
- **Typography:** espécimes com área própria e comparação da escala existente.
  Labels arredondam a duas casas; CSS e detalhes técnicos mantêm os números
  originais. Valores muito pequenos usam algarismos significativos para evitar
  exibir zero incorretamente. Sem escala mapeada, usa fontSize dos estilos existentes.
- **Spacing:** régua com extremos, faixa de destaque do tema e ampliação de 4×
  explicitamente identificada. O valor indicado continua sendo o original.
  Trilhos roláveis recebem foco por teclado; nomes e medidas não dependem só da cor.
- **Borders:** maior respiro e exemplo full em cápsula 120×48 e círculo 48×48,
  ambos com raio calculado de 24px. A amostra full ocupa toda a linha para acomodar
  as duas formas sem comprimir as outras amostras.
- **Elevation:** fundo de inspeção escuro mapeado ao token neutral.800 já existente,
  mantendo superfície, cor e box-shadow originais. O fundo é identificado como
  contexto de inspeção e é configurável, não uma alteração do tema. Mapeamentos
  ausentes geram aviso só em Elevation e usam o fundo original como fallback.

Nenhum token, decisão ou arquivo do POC foi alterado. SHA-256 de tokens.json e
decisions.json permaneceu igual durante a renderização de validação. Cores de
acento e fundos são mapeamentos por caminho, sem valores de fundação transcritos.

## Testes executados

**154 testes aprovados, sem testes ignorados nesta execução:**

| Suíte | Quantidade |
| --- | ---: |
| Python: fundações, inspeção e instalador | 115 |
| Node: modelos/resolver DTCG | 13 |
| Renderer DOM | 24 |
| Adaptadores HTML/React | 2 |

Os testes DOM abrangem o comportamento anterior e os refinamentos: primitivos
únicos nos três modos, filtro independente, escala e precisão tipográficas,
réguas ampliadas, foco/descrição acessível, cápsula/círculo, contexto escuro,
fallback de inspeção e imutabilidade da fonte.

Os dois adaptadores foram empacotados com esbuild e executados em jsdom. Cada uma
das cinco stories HTML renderizou o catálogo; as cinco stories React montaram e
a troca de tema permaneceu funcional. Os adaptadores também verificam a área
única de primitivos e a presença da escala tipográfica. Foi usado o ambiente de
testes já disponível (React/React DOM 18.3.1 e esbuild 0.21.5), sem instalação.

Também executados: node --check, quick_validate.py (skill válida) e detector
mecânico Impeccable (nenhuma ocorrência). A cascata de display da amostra full
foi verificada com getComputedStyle em DOM simulado.

## Renderização com tokens reais do POC

| Story | Resultado nos dois temas | Erros |
| --- | --- | ---: |
| Colors | 24 primitivos únicos + 14 semânticos | 0 |
| Typography | 6 espécimes + 18 amostras de escala | 0 |
| Spacing | 12 réguas | 0 |
| Borders | 20 usos, incluindo cápsulas e dois círculos | 0 |
| Elevation | 8 amostras; fundo escuro rgb(46,46,46) do token existente | 0 |

Os detalhes expansíveis permanecem fechados por padrão. Não há JSON bruto na
apresentação. Valores de tokens recebidos pelo renderer permaneceram idênticos
após as cinco renderizações.

## Reprodução

```bash
python3 -m unittest discover -s tests -q
node tests/storybook/catalog.test.mjs
PRISMO_JSDOM_PATH=/ambiente/node_modules/jsdom node tests/storybook/render.test.mjs
PRISMO_STORYBOOK_TEST_PACKAGE=/ambiente/package.json node tests/storybook/adapters.test.mjs
node tests/storybook/export-preview.mjs /projeto/design-system/tokens.json /tmp/catalog.html
```

Os testes DOM/adaptadores são opcionais se essas dependências não estiverem
presentes; testes ignorados não contam como aprovados.

A prévia interativa gerada em `output/playwright/foundations-preview.html` foi
regenerada e executada em DOM simulado, confirmando uma única área de primitivos.
Pode ser aberta diretamente no navegador, sem servidor. É snapshot descartável
gerado automaticamente, não segunda fonte mantida para as stories.

## Pendências e limites

O socket local continua bloqueado com `Operation not permitted` e o host de
navegador está indisponível. Não foram executados screenshots, medição de layout
em viewport real, revisão visual de sombras/fontes ou build/HMR de Storybook.
A responsividade foi preservada no CSS, mas não é comprovada por jsdom. A percepção
das sombras escuras e eventuais ajustes de fundo devem ser conferidos no navegador
do consumidor. Isso não autoriza modificar os tokens de sombra.

Os novos caminhos `accent`, `typographyScale` e `elevationSurfaces` do exemplo
precisam refletir as convenções do consumidor. Uma escala com px e rem é ordenada
por unidade/valor, sem presumir tamanho de raiz para converter unidades.
