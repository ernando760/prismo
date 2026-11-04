# document — templates visuais: resultados

> Registro histórico da etapa: contagens, bloqueios e pendências abaixo descrevem
> aquela execução. Para o estado de preparação atual, consulte o
> [checklist da release experimental](../docs/experimental-release-checklist.md).

## Alterações

- Três roteiros MDX reutilizáveis: Foundation, Component e Identity.
- DocumentUI.jsx/document.css: estrutura editorial, introdução curta, exemplos com
  legendas, comparações, recomendações, links e detalhes técnicos expansíveis.
- FoundationCatalog adapta o renderer compartilhado das cinco fundações sem alterar
  Storybook/catalog.mjs ou dtcg.mjs. Preserva filtros, comparação de temas e valores
  originais; remove main/h1 próprios para enquadramento dentro da página Docusaurus.
- TokenFacts resolve referências DTCG e apresenta HEX/alpha, px/rem, família/peso,
  tipografia e parâmetros de sombra sem JSON bruto. Precisão/caminhos/aliases ficam
  em detalhes fechados. Arredondamento é só apresentação; não altera a fonte.
- As páginas de componentes recebem exemplos reais por children ou links para o
  catálogo; não incluem implementação paralela de componente de produto.
- Estilos limitados a .prismo-docs herdam variáveis do portal, incluindo tema escuro.
  Layouts e comparações têm regras responsivas; controles mantêm labels e foco.
- Diretrizes de document e guia Docusaurus apontam para document-visual.md sob demanda.
  Templates incompletos não são documentação final: fontes, exemplos e texto devem
  ser adaptados ao contrato aprovado. Lacunas reais permanecem explícitas.

Nenhuma operação fora de document, fundação, token ou decisão foi modificada.
O POC foi consultado em leitura para identificar a apresentação anterior e usar
as dependências instaladas; nenhum arquivo nele foi alterado e nada foi instalado.

## Testes executados

**203 testes aprovados, sem ignorados:**

| Suíte | Testes |
| --- | ---: |
| Python (instalação/operações existentes) | 150 |
| Catálogo: modelos DTCG | 13 |
| Catálogo: renderer DOM | 24 |
| Catálogo: adaptadores HTML/React | 2 |
| Novos templates document | 14 |

Os novos testes verificam SSR sem browser, hidratação sem mismatch, montagem das
cinco fundações, filtro/tema, outline adaptado depois do redraw, atualização derivada
da fonte, precisão preservada, formatação legível, erros por token, fontes ausentes,
exemplo de componente fornecido pelo chamador, links seguros/conhecidos, lacunas,
escaping de texto, controles rotulados e detalhes nativos fechados. Os três MDX
compilaram e renderizaram no servidor.

Também executados:

- Validador de Skill: **Skill is valid!**
- Detector mecânico de UI nos assets: **nenhum achado** (não substitui inspeção visual).
- **Build de produção Docusaurus 3.10.2**, com React 19 e MDX 3, em fixture temporária:
  cinco páginas de fundações, componente, identidade e índice. Compilação client/SSR
  e geração estática concluídas, com links internos, imagens Markdown e anchors em
  modo de erro; nenhuma configuração de checagem foi relaxada.

A fixture tem tokens sintéticos declarados como teste; não representa decisões de
marca ou API de um consumidor. As falhas iniciais do harness foram corrigidas
(configuração incompatível e falta de índice; cache passou a ficar no temporário).
As dependências são reutilizadas em leitura, com caches/artefatos em /tmp.

## Reprodução

```bash
python3 -m unittest discover -s tests -q
node tests/storybook/catalog.test.mjs
PRISMO_JSDOM_PATH=/ambiente/node_modules/jsdom node tests/storybook/render.test.mjs
PRISMO_STORYBOOK_TEST_PACKAGE=/ambiente/package.json node tests/storybook/adapters.test.mjs
PRISMO_DOCUMENT_TEST_PACKAGE=/ambiente/package.json node tests/document/render.test.mjs
PRISMO_DOCUMENT_TEST_PACKAGE=/ambiente/package.json node tests/document/build-portal.mjs
```

O ambiente usado para os testes novos foi prismo-poc/package.json, que já fornece
React/react-dom, esbuild, jsdom, @mdx-js/mdx e Docusaurus/preset-classic. Nenhuma
dependência foi adicionada à Skill. A suíte Node sinaliza skip sem essas dependências;
nenhum teste foi ignorado nesta execução. O harness de build exige os pacotes já
instalados e informa o diretório temporário; não executa npm install.

## Limitações e pendências

A inspeção visual em browser **não foi executada com sucesso**: o host de navegação
estava indisponível e o Chromium local falhou ao iniciar por restrição de sandbox
(Operation not permitted). Não há screenshots aprovados nem validação visual de
contraste, overflow, zoom ou leitores de tela. DOM simulado/build não comprovam
responsividade renderizada ou conformidade WCAG; conferir desktop/mobile e os dois
temas no consumidor continua pendente.

O resolver reutilizado suporta o subconjunto DTCG já existente (sRGB, dimensões
px/rem e tipos das cinco fundações). Formatos não suportados aparecem como pendência;
não foram criados conversores ou tokens novos. Não foram verificados links externos
publicados nem uma API/identidade concreta. Aplicar templates no consumidor ainda
exige investigar suas fontes, propor diffs e obter aprovação.
