# document — portal Docusaurus

Use apenas ao trabalhar no portal, depois de identificar sua versão e configuração.
Confira APIs na documentação oficial compatível com a versão instalada.
Para composição visual e uso dos templates, carregue
[document-visual.md](document-visual.md).

- Leia `docusaurus.config.*`, manifestos/scripts e configuração do plugin docs antes
  de decidir caminhos. `docs/` é convenção, não garantia: respeite `path`, `routeBasePath`,
  múltiplas instâncias, i18n, versionamento e a estrutura atual.
- Reutilize Markdown/MDX, frontmatter, IDs, slugs, categorias e sidebars locais.
  Com sidebar automática, ajuste posição/categoria se necessário; não substitua por
  lista manual. Com sidebar explícita, preserve itens e IDs. Não altere versões
  congeladas/traduções em massa nem gere novos IDs quebrando links sem proposta.
- Use Markdown simples quando bastar. MDX interpreta JSX e chaves: exemplos DTCG
  como `{semantic.color}` e código de props devem estar em code spans/blocos;
  confira compilação. Não importe o componente de produto em MDX se houver
  dependências de browser/providers incompatíveis com build/SSR; prefira exemplos
  de código e links para o catálogo já existente.
- API gerada e catálogos continuam fontes técnicas: adicione orientação e referências,
  sem copiá-los ou refazer os renderers de fundações. Prefira links estáveis validados
  para Storybook/Widgetbook. Reutilize assets aprovados e padrões de acessibilidade.
- Se não houver portal, use `paths.documentation.docusaurus` como raiz proposta
  da aplicação solicitada. Preserve portal existente em outro local e esclareça
  a divergência antes de propor alteração do registro ou instalação. Apresente
  configuração mínima no pacote/local aprovado.
  Antes de executar, confirme gerenciador/lockfile, versão/Node compatíveis e os
  diffs propostos. Não rode gerador sobre árvore não vazia nem aceite defaults que
  sobrescrevam arquivos. Não adicione plugins, busca, deploy ou tema sem necessidade
  aprovada. Reaproveite a identidade do projeto, sem inventar fundações.
- Execute o script de build existente no diretório do portal, com suas verificações
  de links; não relaxe `onBrokenLinks` para obter sucesso. Se o projeto não verifica
  anchors/links de Markdown na versão instalada, use ferramenta existente ou
  inspeção direcionada e declare a cobertura. URL externa indisponível não deve ser
  registrada como validada. Build valida compilação, não exatidão editorial.

Fontes oficiais para consulta conforme a versão:
[Docs](https://docusaurus.io/docs/docs-introduction),
[sidebars](https://docusaurus.io/docs/sidebar),
[MDX](https://docusaurus.io/docs/markdown-features/react).
