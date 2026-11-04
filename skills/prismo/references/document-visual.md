# document — páginas visuais e templates

Carregue esta referência somente ao preparar páginas/templates do portal. Reutilize
primeiro os blocos editoriais já presentes no consumidor. Os assets em
`assets/document/` são uma alternativa pequena, não um tema/Design System novo.

## Composição editorial

Use o título da página do Docusaurus (um h1), introdução curta de finalidade e uma
demonstração cedo. Organize h2 por pergunta de uso: explorar, aplicar, escolher,
comportar, acessar e consultar. Separe seções com espaço e alinhe legendas/medidas;
evite sequência de cards iguais ou parágrafos que escondam decisões. Comparações
servem a diferenças reais, não criam variantes/estados ausentes.

| Página | Demonstração principal | Complemento editorial |
| --- | --- | --- |
| Colors | Paletas primitivas uma vez; semânticos por tema, HEX e alpha | Finalidade dos papéis, aplicações e combinações com contraste verificado |
| Typography | Espécimes e escala comparativa existente | Hierarquia, leitura, estilo por finalidade, limites Web/Flutter |
| Spacing | Réguas e comparação de intervalos | Aplicação em gap/padding/margin; valores/unidades e ampliação da demonstração explícitos |
| Borders | Raios, espessuras, cápsula/círculo para full existente | Finalidade e convenção CSS/Flutter, sem converter full para px arbitrário |
| Elevation | Superfícies e sombras reais por tema | Níveis/finalidades autorizados, camadas legíveis e limites por plataforma |
| Componentes | Exemplos reais de anatomia, variantes/tamanhos e estados | Comportamento, acessibilidade, boas práticas, código de uso e referência de API |
| Identidade | Assets aprovados e aplicações/comparações documentadas | Regras de uso e links para fundações, sem inferir regras pela imagem |

Mostre só tokens relevantes para a página e diferencie primitivos/semânticos.
Valores devem ser legíveis (HEX com alpha separado, px/rem, família/peso, parâmetros
de sombra). HEX pode aproximar sRGB de 8 bits: avise, preserve componentes/precisão
originais e nunca arredonde os tokens para combinar com o rótulo. Tipo não suportado,
alias quebrado ou fonte ausente são avisos visíveis, não `JSON.stringify` ou fallback
inventado. Caminho, alias, precisão e origem ficam em details/summary, fechados por
padrão; a informação essencial de uso continua visível.

## Assets e adaptação mínima

- `Foundation.mdx`, `Component.mdx`, `Identity.mdx`: roteiros MDX compiláveis e
  deliberadamente incompletos. Adaptar imports, título, textos, fontes, exemplos,
  links e seções à proposta aprovada. Não publique instruções de preenchimento como
  documentação concluída. Lacunas reais podem permanecer explicitamente pendentes.
- `DocumentUI.jsx` + `document.css`: layout editorial, exemplos por children,
  comparação, recomendações, detalhes, links e valores DTCG selecionados.
  Não há componente de produto embutido. Use exemplos/catálogos existentes;
  se SSR/providers não permitirem importar um exemplo, use link ou imagem existente
  com descrição/alt útil, sem clonar a implementação no portal.
- `FoundationCatalog` reutiliza `assets/storybook/catalog.mjs` e `dtcg.mjs` sem
  modificá-los. Precisa de tokens reais, config de caminhos e section
  (`colors`, `typography`, `spacing`, `borders` ou `elevation`). `TokenFacts` recebe
  `tokens` e `paths` relevantes. Ambos mostram erros/lacunas; não validam todo DTCG.
  Não há valores de marca predefinidos. O subconjunto do resolver existente aceita
  sRGB e dimensões px/rem; para outros formatos reutilize o conversor do projeto
  ou proponha adaptação, sem criar outra fonte de tokens.

Depois da aprovação, uma disposição possível no portal é
`src/prismo/document/{DocumentUI.jsx,document.css}` e
`src/prismo/storybook/{catalog.mjs,dtcg.mjs}`. Se esses módulos já existirem, ajuste
os imports e reutilize-os. Copiar módulos de apresentação não copia tokens/decisões;
registre a origem e atualização desses arquivos no fluxo existente. Não copie
`tokens.json` ou um novo mapa de valores para a pasta. O MDX deve importar diretamente
as fontes/agregadores e a configuração por caminhos existentes e passar as props.
Reutilize config de caminhos; nunca use o config de exemplo sem conferir o projeto.
Adapte imports MDX ao alias `@site`/convenção local, preservando rotas e IDs.

`document.css` herda variáveis Infima (`--ifm-*`), tipografia e superfícies do portal,
com regras limitadas a `.prismo-docs`. Esses espaçamentos são apresentação editorial,
não novas fundações. Proponha bindings locais se necessário; não troque fontes,
cores de marca ou tema do consumidor. A comparação mantém os valores de cada tema,
incluindo os fundos de inspeção já configurados para Elevation.

## Verificação visual e funcional

Confirme renderização SSR e hidratação: o catálogo usa DOM apenas no efeito; sem JS,
o aviso de carregamento e as informações textuais/TokenFacts continuam presentes.
Confira as cinco fundações, filtro, comparação/tema único, detalhes por teclado,
links reais e exemplos responsivos. Evite main/h1 aninhados: o adaptador reenquadra
o renderer para uso no documento. Não remova rótulos/foco ou use só cor para explicar
recomendações. Compare desktop/mobile nos dois temas, zoom e conteúdo longo; métricas
originais não podem ser alteradas para caber. Execute build MDX/Docusaurus e checks
acessíveis existentes. Build/DOM simulado não substituem inspeção no browser ou
comprovam conformidade completa. Registre o que foi executado e os limites.
