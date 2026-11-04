# foundations — Typography

Siga primeiro [foundations.md](foundations.md) para escopo, checklist, origens e
execução automática. Este guia define as decisões e validações específicas.

## Padrões seguros

Famílias/fallbacks, pesos realmente disponíveis e idiomas/scripts são essenciais:
reutilize evidências ou pergunte, sem baixar/escolher uma fonte de marca. Resolvidas
essas escolhas e sem escala/estilos existentes, use o exemplo abaixo como padrão
estrutural: base 16px, razão 1.25, precisão 4, passos base/large, heading/body,
line-height 1.2/1.5 e tracking -0.02/0. Registre esses parâmetros como `default` e
famílias/pesos como `user`/`existing`; não adote a família fictícia “Example Sans”.
Tracking e métricas ficam pendentes de inspeção real. Não imponha `rem` nem uma
raiz de conversão. Estilos adicionais só se solicitados ou evidenciados.

## Investigar antes de propor

Leia `design-system/decisions.json` (ou caminho documentado pelo projeto) e os
arquivos de tokens indicados nele. Sem registro, informe a ausência e proponha
`init`, sem inicializar silenciosamente. Preserve integralmente Colors e as
decisões anteriores. Carregue esta referência antes de Typography; não execute
Colors nem recalcule outras fundações se isso não foi solicitado.

Busque de forma direcionada famílias, fallbacks, arquivos de fontes, pesos,
tamanhos, line-height, tracking e estilos em CSS/temas, tokens, assets, `pubspec.yaml`
e `TextTheme`/`TextStyle`. Diferencie fontes declaradas de fontes disponíveis.
Leia amostras representativas, não dependências ou todos os componentes. Reutilize
as convenções e os nomes existentes; não crie outra fonte de verdade.

Resolva apenas lacunas essenciais, com perguntas agrupadas:

- Identidade e conteúdo: famílias oficiais/fallbacks, pesos disponíveis, idiomas
  e scripts, textos longos versus interface/marketing. Não escolha ou baixe fontes
  sem autorização nem presuma que pesos sintéticos ou licenças estão disponíveis.
- Escala: base, razão, passos necessários e unidade. Se sugerir valores, explique
  a relação com estilos existentes, hierarquia e densidade; identifique-os como
  propostas, nunca como decisões aprovadas ou exigências universais de WCAG.
- Estilos: quais heading/body/label são necessários, quais passos e famílias
  usam, multiplicador de linha e tracking relativo por papel. Justifique esses
  parâmetros pelas métricas da fonte, tamanho, conteúdo e usos, antes de calcular.
- Plataformas: reutilize o escopo aprovado. Para `rem`, confirme o tamanho de raiz
  usado como referência de conversão para Flutter; não imponha uma raiz ao CSS.

Não repita respostas já fornecidas. Sem famílias/pesos ou outros parâmetros
essenciais que os padrões seguros não resolvam, permaneça em investigação/diálogo.

## Plano e cálculo determinístico

Execute `scripts/typography.py` com Python 3.9+, biblioteca padrão. Todos os parâmetros
são explícitos; a IA decide/proporciona propostas, o script apenas calcula.
Plano ilustrativo reduzido (não uma recomendação de identidade):

```json
{
  "base": {"value": 16, "unit": "px"},
  "ratio": 1.25,
  "precision": 4,
  "root_px": null,
  "steps": {"base": 0, "large": 2},
  "families": {"sans": ["Example Sans", "sans-serif"]},
  "weights": {"regular": 400, "bold": 700},
  "styles": {
    "heading": {"family": "sans", "weight": "bold", "step": "large", "line_height": 1.2, "letter_spacing_em": -0.02},
    "body": {"family": "sans", "weight": "regular", "step": "base", "line_height": 1.5, "letter_spacing_em": 0}
  }
}
```

Guarde a entrada temporária fora do consumidor; o checklist preserva o plano usado.

```bash
python3 /caminho/da/skill/scripts/typography.py --plan /tmp/typography-plan.json
python3 /caminho/da/skill/scripts/typography.py --plan /tmp/typography-plan.json --existing /projeto/tokens.json
```

Saída JSON somente para stdout; nenhuma opção de escrita. Exit 0 significa cálculo
e validação do subconjunto suportado concluídos, não aprovação visual ou WCAG.
Erros retornam 1 sem preview parcial.

Fórmulas e regras de representação:

- `size(n) = base × ratio^n`; razão maior que 1, passos inteiros inclusive negativos.
- `lineHeight` é multiplicador positivo; altura calculada = tamanho final ×
  multiplicador final. `letterSpacing` = tamanho final × `letter_spacing_em`.
  O sufixo `em` descreve a proporção de entrada, não uma unidade DTCG exportada.
- Cálculo decimal com arredondamento `ROUND_HALF_UP`, precisão explícita de 0–8
  casas, inclusive para line-height e tracking. Os cálculos derivados usam o
  tamanho já arredondado/exportado. Resultados positivos que arredondam a zero
  são recusados. Expoentes limitados a -100…100 e contexto de 40 dígitos limitam
  custo/representação numérica; esses limites não são regras de design.
- Dimensões DTCG: `px` ou `rem`, nunca `em`, `sp` ou `dp`. Base e razão não podem
  ser zero, negativas ou não finitas. Para base `rem`, `root_px` é obrigatório;
  para `px`, pode ser `null`. Estilos existentes em rem também precisam de raiz
  explícita para a projeção Flutter. Não escolha um valor arbitrário para satisfazê-la.

## Tokens e reutilização

A saída resumida contém `token_changes`, `scale`, `styles` resolvidos e `reused`;
`--full` inclui também o documento completo em `tokens`. Novos primitivos:
`primitive.typography.{family,weight,size,lineHeight,letterSpacing}`. Novos estilos:
`semantic.typography.<papel>` com `$type: typography` e os cinco campos DTCG
`fontFamily`, `fontSize`, `fontWeight`, `letterSpacing`, `lineHeight`, por aliases.
Line-height primitivo é `number`; tamanho/tracking são `dimension`; família e peso
usam os tipos `fontFamily` e `fontWeight`. Não adicione cores ao composite typography.

`families` e `weights` aceitam valores ou aliases `{caminho}` de tokens existentes.
Um estilo pode ser diretamente um alias de typography existente; nesse caso
`steps`, `families` e `weights` podem ficar vazios. Quando nomes já existem e seus
valores resolvidos coincidem, são preservados, inclusive metadados. Valores iguais
do mesmo tipo reutilizam aliases; dimensões px/rem não são igualadas implicitamente.
Conflitos de nome/valor, aliases ausentes/circulares ou tipos incompatíveis são
recusados. Não apague tokens existentes nem use nomes alternativos só para ocultar
um conflito: proponha reutilização ou uma alteração específica aprovada.

`--existing` preserva Colors e os demais tokens no documento retornado, sem mutar
a entrada. A validação abrange apenas os tipos/aliases tipográficos emitidos ou
reutilizados, não o documento DTCG inteiro. Resolve aliases `{caminho}` e tipos
herdados; não resolve `$extends`, JSON Pointer/$ref ou arrays com referências.
Composites typography reutilizados precisam dos cinco campos suportados. Tokens
CSS/Dart legados exigem mapeamento revisado em cópia temporária. Não os migre no
consumidor automaticamente. Em projetos com múltiplos arquivos, não sobrescreva um
arquivo parcial com o documento combinado do preview.

## Legibilidade, Web e Flutter

A projeção `web` mantém as dimensões e o multiplicador sem unidade. Em Web,
prefira unidades relativas quando adequadas ao projeto e preserve a possibilidade
de ampliar texto e alterar espaçamento. `heading` é um papel visual, não substitui
hierarquia semântica de headings HTML ou semântica de acessibilidade Flutter.

A projeção `flutter` é numérica: tamanho e tracking em pixels lógicos, `height`
como multiplicador. Conversão `rem → lógico` = dimensão exportada × `root_px`.
É uma referência de mapeamento, não código Dart pronto ou equivalência de
renderização. Famílias/fallbacks precisam de mapeamento aos assets disponíveis;
genéricos CSS não viram fontes Flutter automaticamente. Pesos numéricos precisam
ser mapeados às opções da API e fontes/variações disponíveis, sem arredondamento
silencioso. Respeite `TextScaler` do sistema; não desative ou duplique a escala.

Aprovação matemática não comprova legibilidade: validar métricas, acentos, scripts,
fontes de fallback e pesos, densidade de conteúdo e quebras de linha em uso real.
Tracking negativo e linhas apertadas exigem verificação visual. WCAG não define
um tamanho mínimo universal nem exige usar os valores de override como padrão:
verifique resize a 200% (1.4.4) e, nos contextos aplicáveis, override de line-height
1.5, tracking 0.12em, word-spacing 0.16em e espaço após parágrafos 2em sem perda
(1.4.12). O script não mede layout, clipping ou conformidade desses critérios.

## Validar e persistir

Apresente base/razão/unidades/arredondamento e justificativas, tabela da escala,
famílias/pesos, heading/body/label solicitados com tamanho, altura de linha e
tracking, aliases reutilizados e projeções Web/Flutter. Inclua limites e pendências,
amostras visuais quando houver fontes e ambiente para renderizá-las. Não declare
validação visual se apenas calculou números.

Use o checklist de `foundations.md` para persistir adições e registrar suas origens
sem aprovação repetida. Conflitos exigem esclarecimento antes de alterar.
Após validar, grave somente os tokens solicitados e acrescente
`foundations.typography` no registro, preservando `init`,
`foundations.colors` e outras seções. Registre plano, fontes/evidências, justificativas,
caminhos, aliases, arredondamento, conversão de unidade, verificações executadas e
pendências. Não instale fontes ou ferramentas como consequência da criação de fundações.

Leia de volta os arquivos finais, resolva os aliases tipográficos e recalcule
usando o plano aprovado e os tokens persistidos. Confira o diff para garantir
preservação das demais fundações. Entregue a localização do registro e diferencie
preview de persistência e cálculos de validação visual/acessível.

Fontes: [DTCG Typography](https://www.designtokens.org/tr/2025.10/format/#typography),
[WCAG Text Spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html),
[Resize Text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html),
[Flutter height](https://api.flutter.dev/flutter/painting/TextStyle/height.html),
[letterSpacing](https://api.flutter.dev/flutter/painting/TextStyle/letterSpacing.html)
e [TextScaler](https://api.flutter.dev/flutter/painting/TextScaler-class.html).
