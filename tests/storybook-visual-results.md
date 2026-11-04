# Atualização visual do catálogo Storybook

## Alterações compartilhadas

O renderer em `skills/prismo/assets/storybook/catalog.mjs` passou a usar layouts
específicos para cada fundação, mantendo `renderFoundations(tokens, config, options)`
e os mesmos templates HTML e React.

- Colors: grids de paletas, grupos primitivos/semânticos, HEX e alpha, sem texto
  sobre as cores. HEX de 8 bits aproximado é identificado nos detalhes; a amostra
  continua usando o valor sRGB exato.
- Typography: espécimes de heading/body/label e propriedades formatadas de família,
  tamanho, peso, linha e tracking, com fallbacks aprovados quando mapeados.
- Spacing: réguas com origem comum, agrupadas por uso, com dimensões exatas e
  trilhos roláveis para valores maiores que a área disponível.
- Borders: amostras comparativas de raios/espessuras, incluindo zero e full.
- Elevation: cards sobre superfícies dos temas e métricas legíveis por camada.
- JSON bruto removido. Caminhos, tipos, aliases e CSS técnico ficam em details
  nativos, fechados por padrão e acessíveis por teclado.
- Grids fluidos, comparação em duas colunas acima de 1000px e uma coluna abaixo,
  controles com altura mínima de 44px, foco visível e metadados sem opacidade reduzida.

A paleta do chrome do visualizador é separada dos espécimes; os valores das
fundações vêm exclusivamente da fonte DTCG. Não houve alteração dos tokens,
decisões ou configuração do POC, nem instalação de pacotes.

## Verificações executadas

**145 testes aprovados:**

| Suíte | Testes |
| --- | ---: |
| Python, incluindo fundações e instalador | 115 |
| Node: resolver/modelos DTCG | 13 |
| DOM simulado: renderer compartilhado | 15 |
| Integração dos templates HTML e React | 2 |

Os testes DOM verificam grupos de paletas, HEX/alpha, propriedades formatadas,
medidas reais, aliases recolhidos, preservação de valores, filtro, troca de tema,
erros e ausência de injeção HTML. Não são testes de pixels ou layout.

Os adaptadores foram empacotados com esbuild e executados em jsdom. Cada uma das
cinco exports HTML retornou o novo DOM; as cinco exports React foram montadas por
React DOM, incluindo atualização compare → dark. Foram usados React/React DOM
18.3.1, esbuild 0.21.5 e jsdom já disponíveis no ambiente, sem novas instalações.
Isso verifica os adaptadores e o renderer, não o build de um Storybook real.

Também executados: node --check, quick_validate.py da skill e detector mecânico
Impeccable (nenhuma ocorrência). A API pública e os imports dos dois templates
permaneceram os mesmos.

Com os tokens reais do POC, em leitura:

| Story | Amostras nos dois temas | Erros |
| --- | ---: | ---: |
| Colors | 62, em seis grids | 0 |
| Typography | 6 | 0 |
| Spacing | 12 | 0 |
| Borders | 20 | 0 |
| Elevation | 8 | 0 |

As 108 amostras possuem detalhes técnicos recolhidos. O objeto de tokens
permaneceu idêntico após renderização. A prévia HTML autônoma também foi executada
em DOM simulado e gerou os dois painéis.

Cálculos de contraste sobre os valores usados pelo chrome:

| Par | Razão |
| --- | ---: |
| Texto #182230 / fundo #F8FAFC | 15.318:1 |
| Texto secundário #475467 / fundo #F8FAFC | 7.347:1 |
| Limite de controles #667085 / fundo #FFFFFF | 4.975:1 |

O texto dos temas do POC mantém suas cores de origem; a razão texto/background é
19.750:1 em ambos os temas. Esses cálculos não equivalem a uma auditoria completa
de acessibilidade de todos os estados ou de outros projetos consumidores.

## Reprodução e artefato

```bash
python3 -m unittest discover -s tests -q
node tests/storybook/catalog.test.mjs
PRISMO_JSDOM_PATH=/ambiente/node_modules/jsdom node tests/storybook/render.test.mjs
PRISMO_STORYBOOK_TEST_PACKAGE=/ambiente/package.json node tests/storybook/adapters.test.mjs
node tests/storybook/export-preview.mjs /projeto/design-system/tokens.json /tmp/catalog.html
```

Os testes DOM/adapter são opcionais quando suas dependências não estão disponíveis;
nesse caso são ignorados e não devem ser contados como aprovados. Nenhuma delas
é adicionada como dependência de produção ao Prismo.

Artefato gerado nesta sessão: `output/playwright/foundations-preview.html`.
Abra em um navegador, sem servidor: é uma prévia interativa com snapshot gerado
automaticamente dos tokens. Não é uma segunda fonte mantida para as stories e
precisa ser regenerado após mudanças. Não carrega fontes externas automaticamente.

## Limites da validação

A criação de socket local continua bloqueada (`Operation not permitted`) e o host
de navegador está indisponível. Portanto, screenshots, inspeção visual desktop/mobile,
medidas de layout real, fontes efetivamente renderizadas, HMR e build real do
Storybook não foram executados/aprovados. As regras responsivas foram implementadas,
mas o DOM simulado não calcula seu layout como um navegador.
