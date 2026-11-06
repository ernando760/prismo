# document — documentação do Design System

Consulte [naming.md](naming.md) quando houver convenção de tokens a registrar ou aplicar; preserve decisões e nomes existentes.

## Investigar o escopo e as fontes

Leia as instruções locais e o registro de decisões aprovado, normalmente
`design-system/decisions.json`. Investigue só o assunto/pacote pedido: fundações,
fontes DTCG (inclusive arquivos divididos e aliases), componentes reais, testes,
docs, identidade visual e catálogos existentes. Consulte apenas as seções relevantes;
não carregue referências de foundations/create para apenas descrever seus resultados.
Sem escopo explícito, faça inventário curto e proponha prioridades, sem documentar
a biblioteca inteira por padrão.

Localize o pacote Docusaurus, sua versão, configuração, plugin de docs, caminhos,
sidebars, idiomas, versões e convenções editoriais. Em monorepo, o portal pode estar
fora do pacote de componentes. Dependência declarada ou arquivo de configuração
isolado não comprovam portal funcional. Preserve configurações e conteúdo existente.

Para cada página, identifique fonte canônica, público e lacunas. Procure páginas,
README, API gerada, comentários e stories equivalentes antes de escrever.
Docusaurus centraliza navegação e orientação de uso; API técnica pode continuar
na fonte existente, com link contextual. Não copie tabelas de props geradas nem
transcreva valores DTCG em constantes, CSS ou um segundo JSON. Para tabelas de
valores, reutilize a geração existente ou proponha derivação mínima da fonte com
comando de atualização; trechos estáticos devem ser identificados como exemplos,
com origem e forma de conferência. Não crie pipeline novo sem necessidade.

Pergunte apenas o que faltar no projeto ou conversa, agrupando por escopo/público,
conteúdo/identidade e portal/publicação. Distinga fatos observados, decisões
aprovadas, recomendações e informações desconhecidas. Não deduza regras de marca
ou conformidade acessível a partir de aparência/código. Divergência entre decisões,
tokens e implementação é uma pendência a esclarecer, não licença para corrigir
fundações ou componentes. Sem registro, procure outra fonte aprovada antes de pedir
informação; documentar não inicializa decisões nem executa outras operações.

## Propor antes de modificar

Apresente uma proposta concreta com:

- Páginas a criar/atualizar e navegação, público e finalidade de cada uma;
  demonstrações visuais, aplicações e comparações úteis, reutilizando exemplos reais.
- Fontes e conteúdo a reutilizar por links/geração; diferenças para docs existentes.
- Arquivos/diffs, lacunas e perguntas impeditivas; seções que ficarão explicitamente
  pendentes e seu impacto, sem preencher decisões por suposição.
- Links de Storybook/Widgetbook conhecidos, verificações e comandos previstos.
- Se faltar Docusaurus: local do portal, versão compatível, dependências, scripts,
  configuração mínima e impacto em manifestos/lockfile/navegação. Pergunte se essa
  configuração deve ser realizada agora. Não execute scaffolding ou instalação
  antes da aprovação explícita desse escopo. Se recusado/adiado, entregue proposta
  e pendências; só produza docs em outro destino se isso também for autorizado.

Aguarde aprovação antes de criar/editar arquivos do consumidor, inclusive Markdown,
sidebars e configuração. Aprovação anterior de create/foundations, silêncio ou saída
do inventário não aprovam document. Uma aprovação pode cobrir conteúdo e setup se
ambos estiverem apresentados. Reapresente mudanças materiais de escopo/destino.

## Escrever após aprovação

Carregue [document-docusaurus.md](document-docusaurus.md) somente ao preparar ou
alterar o portal. Para páginas visuais, siga o guia de templates indicado ali:
priorize demonstrações, valores legíveis e diretrizes; detalhes técnicos expansíveis
ficam em segundo plano. Adapte o conteúdo ao projeto; as listas abaixo são critérios de
cobertura, não uma exigência de criar uma página por item.

| Conteúdo | Cobertura e fonte |
| --- | --- |
| Fundações | Finalidade, papéis primitivos/semânticos, temas, aliases, uso e restrições; valores da fonte DTCG e decisões existentes, sem recalcular escalas |
| Componentes | Anatomia/slots, props tipadas/defaults/eventos, variantes/tamanhos, estados, comportamento, teclado/foco, nome/semântica acessível, uso recomendado/evitar e limitações; API e testes reais |
| Identidade visual | Marca/assinaturas aprovadas, cores e tipografia, composição e aplicações Web/Flutter/Marketing conforme escopo; assets e diretrizes autorizados |

Marque itens não aplicáveis com motivo; itens desconhecidos como pendentes. Se a API
ou identidade não estiver definida, peça definição em vez de projetá-la durante a
documentação. Exemplos devem usar exports e tokens/bindings existentes; não implemente
componentes nem instale ferramentas de catálogo como efeito colateral.

Referencie stories/use-cases reais, com nome, finalidade e link disponível. Confirme
base URL/ID/rota, ambiente e versão; não invente URL publicada a partir de arquivo
local. Sem URL, registre caminho e comando local conhecidos e marque publicação
pendente. Prefira links a embeds; iframe exige necessidade, título acessível e
verificação de política de carregamento. Não tente executar Flutter/Dart no MDX.

## Validar e entregar

Confira fontes contra conteúdo: props/defaults, exemplos/imports, aliases/temas,
limitações e recomendações devem ser rastreáveis. Verifique links internos, anchors,
assets, navegação, exemplos e MDX com as ferramentas já existentes. Execute o build
do portal e lint/typecheck/testes de exemplos quando aplicáveis; confira as páginas
alteradas no browser quando disponível, incluindo navegação por teclado, headings,
links descritivos, texto alternativo e apresentação responsiva. Não declare WCAG
completa por build ou teste automatizado.

Reporte arquivos, fontes reutilizadas, comandos/resultados e lacunas. Sem ferramenta,
rede ou runtime, informe a checagem bloqueada; não conte como aprovada. Confira que
tokens, decisões e componentes foram preservados, exceto alterações explicitamente
propostas/aprovadas. Não publique/deploy como consequência de documentar.

## Inventário opcional, somente leitura

```bash
python3 /caminho/da/skill/scripts/document.py /projeto
# Registro em outro caminho relativo:
python3 /caminho/da/skill/scripts/document.py /projeto --decisions ds/decisions.json
```

O helper localiza candidatos de fontes, configurações e manifestos sem executar JS,
comandos ou instalações. Não lê conteúdo técnico completo, resolve aliases, interpreta
configuração dinâmica ou avalia aprovação/qualidade editorial. Informa limites da
busca e lacunas; em monorepos grandes execute também no pacote escolhido, sem
interpretar inventário parcial como ausência. A investigação e a proposta continuam
responsabilidade do agente. Exit 0: inventário produzido, não validação/aprovação;
exit 1: entrada inválida ou erro de leitura.

Em projetos novos, sugira `docs/docusaurus`, `docs/storybook` e `docs/widgetbook`
para as ferramentas adotadas, com nomes e caminhos sujeitos à aprovação. Reutilize
aplicações existentes e trate qualquer mudança de diretório como migração separada.
Catálogos consomem a biblioteca por sua API pública; não são fonte dos componentes.

O inventário apresenta `declared_documentation` com as raízes registradas e sua
existência. Antes de propor instalação use o caminho da ferramenta correspondente;
a presença do diretório não comprova configuração nem build. Divergências com uma
instalação existente exigem decisão explícita, não migração automática.

Mostre nomes e significados somente a partir das fontes de tokens e decisões aprovadas; se não houver significado documentado, registre a lacuna.

## Cobertura de Colors

Use [colors-coverage.md](colors-coverage.md) para documentar cobertura funcional
e de evolução, usos por tema, exceções e motivos de adiamento. Publique resumos
e links aos detalhes de aliases, valores e evidências; não regenere escalas nem
crie aliases para completar a documentação. Diferencie cálculo, inspeção visual
real e conformidade. Registro legado sem matriz tem cobertura desconhecida.
