# Visualização de fundações no Storybook

Integração inicial de visualização, não uma nova operação de componentes. Use
quando pedirem visualizar/publicar as fundações no Storybook, inclusive como
continuação de foundations. Carregue só esta referência, não os cinco guias de
cálculo. Não implemente componentes nem configure Docusaurus/Widgetbook.

## Investigar e autorizar

Leia decisões, caminhos de tokens e instruções locais. Confirme Web no escopo e
investigue manifestos, workspaces, scripts, configurações main/preview, renderer,
builder, versão e glob de stories. O helper usa `paths.documentation.storybook` como raiz do manifesto e procura
`.storybook` dentro dela; argumentos explícitos sobrescrevem esses valores. Sem
registro, mantém a raiz do projeto e `.storybook` legados:

```bash
python3 /caminho/da/skill/scripts/storybook.py /projeto
# Caminhos customizados quando conhecidos:
python3 /caminho/da/skill/scripts/storybook.py /projeto --config-dir config/storybook --decisions docs/decisions.json
```

Web declarado não prova aplicação existente. Storybook planejado em decisões não
aprova instalação. Config encontrada não comprova que o build funciona. Em monorepo,
inspecione o pacote Web correspondente. Sem Web no escopo, explique e não instale.
Se não houver informações, pergunte só qual projeto/pacote e framework usar.

Para uma instalação nova solicitada, use a raiz registrada em
`paths.documentation.storybook`. Se houver configuração existente em outro local,
investigue e proponha reutilização ou alteração explícita do registro; não mova nem
crie uma segunda instalação silenciosamente. Inclua o caminho de configuração real,
globs e dependência da biblioteca selecionada na proposta.

Se Storybook estiver ausente ou precisar de nova configuração, apresente uma
proposta concreta: framework/builder compatível com o projeto, versões/requisitos
consultados na documentação oficial, gerenciador/lockfile existentes, dependências,
scripts, arquivos e diffs. Solicite aprovação e espere antes de instalar/configurar.
Não execute `init`, instalação ou upgrade silencioso, inclusive se o CLI sugerir.
Sem framework Web existente, não escolha React ou outro framework automaticamente.

Com Storybook existente, preserve renderer, addons, temas, globs, stories e scripts.
Não substitua main/preview nem mude major/builder para acomodar esta integração.
Inspecione diffs e aprove alterações de arquivos existentes quando necessário.

## Recursos e fonte da verdade

Em `assets/storybook/`:

- `dtcg.mjs`: resolução DTCG e projeção CSS, sem biblioteca externa.
- `catalog.mjs`: renderer DOM para os cinco catálogos, comparação e filtro.
- `catalog.config.mjs`: exemplo de mapeamento só por caminhos, sem valores de tokens.
- `Foundations.stories.js`: CSF para renderer HTML que aceita HTMLElement.
- `Foundations.react.stories.js`: alternativa de adaptador para renderer React.

Copie apenas os recursos necessários para um local compatível com o consumidor,
sem sobrescrever arquivos. Escolha **um** template de stories; os dois têm o mesmo
título e não devem ser registrados juntos. Não instale @storybook/html-vite em um
Storybook React existente. Para Vue/Angular/Svelte, adapte apenas o wrapper DOM ao
ciclo de montagem/desmontagem do renderer, sem migrar o projeto; esses wrappers
não estão prontos/validados nesta versão.

Troque o import `./tokens.json` da story pelo caminho real da fonte DTCG. **Não
copie tokens para a pasta de stories**, não transcreva valores e não gere uma
segunda paleta. Import JSON estático permite atualização/rebuild pelo builder;
verifique HMR no projeto. Para múltiplos arquivos, use o agregador existente ou
importe/mescle objetos explicitamente em memória, recusando colisões. Nunca una
por spread superficial se isso perder grupos. Não escreva um bundle de tokens
como segunda fonte mantida manualmente.

Adapte `catalog.config.mjs` aos nomes reais: prefixes das coleções e caminhos de
background/surface/text/border de cada tema. `{theme}` nos prefixes é substituído
por light/dark; não é sintaxe DTCG de modos. Temas com fontes em documentos distintos
exigem adaptar a seleção do documento no wrapper antes de renderizar cada tema.
Essa adaptação não está pronta no template inicial, que usa grupos de um documento.
O campo opcional `fontFallback` pode apontar para um token fontFamily adicional
aprovado nas decisões; é combinado só na projeção, sem reescrever o composite.
Não simule tema ausente com valores inventados nem renomeie tokens para encaixá-los.

Collections separam colors, typography, typographyScale, spacing, radius, width e
elevation. typographyScale aponta às dimensões de tamanho existentes; sem elas,
a comparação usa fontSize dos estilos sem inventar novos tamanhos. Os rótulos
tipográficos arredondam a duas casas, mas CSS e detalhes usam a precisão original. Temas
podem compartilhar tokens globais de tipografia/espaçamento/bordas, enquanto cores
e sombras usam caminhos específicos. Prefixes não encontrados mostram estado vazio;
alias inválido mostra erro. Tema não mapeado não é substituído pelo outro tema.
Sem superfícies mapeadas, o catálogo identifica o uso de Canvas/CanvasText de
apresentação; isso não constitui decisões de identidade ou tema aprovado.

## Conteúdo exibido

- Colors: primitivas em uma área compartilhada única, independente da seleção de
  tema; a comparação claro/escuro contém apenas cores semânticas. Grids com HEX derivado
  dos componentes e alpha legível. HEX de 8 bits pode ser aproximado; a amostra
  continua usando os componentes exatos. Caminhos e aliases ficam em detalhes.
- Typography: espécimes com hierarquia e propriedades formatadas de famílias/pesos,
  tamanho, tracking e multiplicador de linha do
  composite. Reutilize carregamento de fontes/assets do projeto; não baixe fontes.
  Sem a fonte disponível, navegador pode usar fallback e a aparência não comprova
  a tipografia aprovada. Preserve fallbacks adicionais registrados nas decisões.
- Spacing: réguas ampliadas 4× e identificadas como tal, com extremos e destaque
  por accent do tema; medidas originais permanecem ao lado, sem alterar tokens.
  O caminho accent em cada tema é opcional e usa currentColor na ausência.
  Trilhos permitem rolagem por teclado de valores longos.
- Borders: grids comparativos de raios e espessuras; full mostra cápsula 120×48
  e círculo 48×48, ambos derivados do number 0.5 na geometria da amostra. Confira o contrato full aprovado do consumidor; não o substitua nos
  componentes. A visualização não cria componentes de produção.
- Elevation: cards sobre superfícies de cada tema, box-shadow e métricas por camada,
  inclusive inset; lista vazia significa none.
  O mapeamento opcional elevationSurfaces por tema fornece caminhos de background,
  surface e text para o contexto de inspeção. O exemplo usa primitive.neutral.800
  como fundo escuro; adapte ao projeto, sem gerar cores ou modificar o tema.
  Falhas nesse mapeamento são avisadas só em Elevation, com fallback às superfícies
  originais. As limitações Flutter não se aplicam à renderização CSS, mas permanecem registradas.

Valores são formatados para leitura; não exiba JSON bruto nas amostras. Os detalhes
expansíveis mostram caminho, tipo e alias; tipografia/sombras têm propriedades
legíveis. O chrome do catálogo é de apresentação, não uma nova fonte de tokens.

São cinco stories CSF, com `mode` compare/light/dark e controles locais de tema e
filtro. A comparação é no canvas, independente da aparência do manager Storybook;
backgrounds addon sozinho não troca tokens semânticos. Não instale addon de temas
para esta primeira integração. CSS de apresentação fica escopado ao catálogo;
valores de layout do visualizador não são tokens das fundações.

O resolver suporta aliases `{caminho}`, tipos herdados, $root e composites
color/dimension/typography/shadow, incluindo referências de componentes. Cores
são sRGB, dimensões px/rem; arrays de shadows não são achatados. Não resolve
$extends/JSON Pointer, DTCG Resolver modes ou transformações legadas. Mostre os
limites; não converta fontes silenciosamente nem declare validação DTCG completa.

## Verificar e registrar

Após integração autorizada, rode o build real do Storybook na versão do consumidor.
Abra as cinco stories, compare temas, filtre nomes, confira vazios/erros e viewport
estreito. Compare amostras com tokens resolvidos e fontes carregadas. Altere um
valor apenas numa cópia temporária de teste e confirme propagação sem editar as
stories. Confira alias/tema ausente como erro visível e CSS sem vazamento.

Releia o diff: tokens, decisões anteriores e outras stories preservados. Se registrar
a integração em decisões, acrescente somente caminhos da fonte, mapeamento,
renderer/versão, stories, verificações e limitações, sem reescrever fundações.
Não declare build, HMR ou validação visual aprovados sem executá-los. Informe
bloqueios concretos; teste de resolver/sintaxe não comprova build ou browser.

Fontes: [Storybook CSF](https://storybook.js.org/docs/api/csf),
[Args](https://storybook.js.org/docs/writing-stories/args),
[Instalação](https://storybook.js.org/docs/get-started/install/).

Para catálogo aninhado, passe `--config-dir docs/storybook/.storybook` e
`--package-dir docs/storybook` ao helper, ajustando aos caminhos aprovados. O
manifesto inspecionado é o do catálogo; o componente deve ser importado da API
da biblioteca. Não mova configurações existentes sem proposta separada.
