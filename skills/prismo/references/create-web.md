# create — Web

Carregue após aprovação da proposta Web. Siga framework, linguagem, estilos,
exports e arquitetura de estado existentes. Preserve SSR/hidratação quando houver.
Prefira elementos HTML nativos para semântica e interação; reutilize as primitivas
acessíveis já adotadas. ARIA não substitui comportamento de teclado. Para widgets
compostos, consulte só o padrão APG pertinente, sem criar dependência de biblioteca.

## Implementação e catálogo

Mapeie anatomia/variantes/tamanhos/estados para os tokens e bindings já existentes.
Mantenha limites de conteúdo e estado controlado/não controlado conforme contrato;
não imponha ambos. Evite booleanos redundantes, APIs polimórficas e abstrações sem
uso aprovado. Preserve comportamento de forms, links e eventos nativos aplicáveis.

Crie stories no renderer Storybook e versão instalados, importando o componente
real. Reutilize providers/temas/globs e fixtures existentes. Mostre os estados e
combinações pertinentes, textos longos, temas aprovados e cenários de erro quando
aplicáveis. Configure args/controles úteis, sem simular semântica por CSS.
Use play/interação e a suíte local para asserções observáveis (nome/role, ação,
foco, teclado, estado, disabled/loading/validação quando existirem). Não copie os
renderers de fundações para fingir um catálogo de componentes.

Se Storybook não existir, proponha a configuração mínima compatível e obtenha
aprovação antes de instalar/configurar. Não troque builder/renderer ou faça upgrade
incidental. Ausência de runtime não autoriza entregar story não executada como validada.

## Verificações e documentação

Execute testes reais com a ferramenta do projeto. Se houver axe/addon acessível,
reutilize-o; se faltar, proponha a dependência necessária ou execute checagens
aplicáveis com ferramentas existentes, deixando a cobertura faltante explícita.
Scanners automáticos não comprovam conformidade completa.

Conforme o componente, verifique nome/role/estado, labels e erros, ordem/visibilidade
de foco, operação por teclado, foco após fechar/abrir overlays, contraste, alvo,
zoom/reflow e preferências de movimento. Exercite estados por eventos reais;
não afirme que disabled funciona só porque há classe visual. Valide no browser
quando layout, foco nativo ou navegação exigirem; jsdom não os comprova integralmente.
Execute build/typecheck e o build real do Storybook, conforme scripts existentes.

Documente props/defaults/eventos, exemplos, variantes/estados, requisitos de labels,
comportamento por teclado, tokens utilizados e limitações. Use docs locais ou
MDX já adotado, sem instalar ferramenta documental nova.

Fontes: [APG](https://www.w3.org/WAI/ARIA/apg/patterns/),
[Storybook interactions](https://storybook.js.org/docs/writing-tests/interaction-testing),
[acessibilidade](https://storybook.js.org/docs/writing-tests/accessibility-testing).

## Pacotes distribuíveis

Quando o componente pertencer a uma biblioteca distribuível, inclua na proposta
os formatos/entradas públicos e os consumidores suportados. `private: true` não
exclui bibliotecas internas distribuídas por tarball. Build do Storybook ou import
via alias de workspace não comprova consumo do pacote publicado.

Após a implementação aprovada, valide nesta ordem, usando ferramentas existentes:

1. Execute o build da biblioteca e gere um tarball real com `npm pack --json
   --pack-destination /tmp/diretorio-existente` (ou equivalente do gerenciador local).
   Revise scripts de lifecycle e use saída/cache temporários. Não publique.
   `--dry-run` ajuda a inspecionar, mas não substitui testar o tarball produzido.
2. Confira o manifesto e os arquivos **dentro do tarball**: `files`/ignore,
   `main`/`module`/`types` legados e `exports` (raiz, subpaths e condições suportadas).
   As entradas JS, declarações e CSS devem existir no pacote, sem depender de `src`
   omitido, aliases locais ou dependências de desenvolvimento transitivas.
3. Instale o tarball em consumidor temporário fora do workspace; sem symlink para
   a biblioteca nem `paths` que desviem seus imports. Importe pelo nome público e
   subpaths aprovados, execute o JS e confira símbolos/contrato. Teste ESM e CJS
   somente quando declarados; não imponha pacote dual a biblioteca ESM.
4. Se houver TypeScript, consuma as declarações emitidas com `tsc --noEmit`,
   `skipLibCheck: false`, importando valores **e tipos** públicos. Para NodeNext
   use `module: NodeNext` e `moduleResolution: NodeNext`; para Bundler use
   `module: ESNext` e `moduleResolution: Bundler`, com versão instalada compatível.
   Exercite os modos declarados como suportados (normalmente ambos em biblioteca
   Web) e justifique os não aplicáveis. Imports relativos ESM nas declarações
   precisam de extensões compatíveis com NodeNext; `./Button` pode passar no
   Bundler e falhar no NodeNext. Não esconda a falha com `skipLibCheck` ou `paths`.
5. Se houver CSS, resolva o subpath público e faça o bundle do consumidor com
   import do CSS pelo pacote. Confira CSS emitido, assets/URLs e preservação por
   tree shaking/`sideEffects` conforme a ferramenta; importe em runtime/browser
   quando necessário. `tsc` e Node sozinhos não validam aplicação de estilos.

Registre comandos, versões, entradas e resultados separados para build, pack,
exports/runtime, tipos, CSS e cada resolução; ferramenta ausente é bloqueio
explícito. Preserve formatos existentes: corrija apenas o contrato suportado.
Não instale outro compilador/bundler nem amplie a matriz só para esta verificação.

No helper opcional, planos antigos continuam aceitos. Para revisar cobertura de
um pacote Web, acrescente `distribution` com `typescript` e `css` booleanos e
`resolutions` como lista sem repetições de `NodeNext`/`Bundler`. Exemplo:
`{"typescript": true, "css": true, "resolutions": ["NodeNext", "Bundler"]}`.
Declare em `checks` os kinds `build`, `pack`, `exports` e, conforme o contrato,
`types`, `css`, `nodenext`, `bundler`, com comandos concretos no contexto correto.
O helper exige essa cobertura quando o contrato é fornecido; não executa checks
nem atesta o tarball. Sem esse campo, emite aviso ao detectar entradas públicas;
a investigação continua necessária para bibliotecas sem manifesto completo.

Fontes: [npm pack](https://docs.npmjs.com/cli/v11/commands/npm-pack/),
[resolução de módulos TypeScript](https://www.typescriptlang.org/docs/handbook/modules/reference.html#the-moduleresolution-compiler-option).
