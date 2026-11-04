# foundations — Elevation

## Investigar e esclarecer

Leia `design-system/decisions.json` (ou caminho documentado) e os tokens indicados.
Sem registro, informe a ausência e proponha `init`, sem inicializar silenciosamente.
Busque sombras, camadas, cores/alpha e usos em CSS, temas, BoxShadow e elevação
Material. Use amostras representativas, excluindo dependências. Um valor Material
`elevation` não é uma receita BoxShadow/CSS nem autoriza copiá-lo como blur.
Registre fontes e reutilize nomes e padrões aprovados, preservando as fundações.

Pergunte apenas pelas lacunas: finalidades e hierarquia dos níveis; cor/alpha e
preferências de intensidade por tema; deslocamentos, blur, spread e camadas;
restrições de plataforma/performance; unidade, arredondamento e conversão rem.
Não repita respostas nem invente valores para preencher `low/medium/high`. Esses
nomes são opcionais; proponha só níveis com usos reais, preferindo poucas camadas
necessárias. Sem critério existente de intensidade/custo, justifique a proposta e
registre a necessidade de revisão visual/performance, sem impor limiares arbitrários.
Carregue só esta referência; não execute nem altere outras fundações.

## Plano e cálculos

Use `scripts/elevation.py`, Python 3.9+ e biblioteca padrão. Exemplo matemático:

```json
{
  "unit": "px",
  "root_px": null,
  "rounding": {"mode": "half_up", "increment": 0.25},
  "opacity_precision": 4,
  "levels": {
    "none": [],
    "low": [{"color": "#000000", "opacity": 0.12, "scale": 1, "inset": false, "offsetX": 0, "offsetY": 1, "blur": 2, "spread": 0}]
  },
  "semantics": {"flat": "{primitive.elevation.shadow.none}", "card": "{primitive.elevation.shadow.low}"}
}
```

Todos os parâmetros são explícitos, não recomendações universais. Uma camada
calcula cada dimensão como `parâmetro × scale`, depois arredonda ao incremento
na unidade escolhida. O fator scale é não negativo e não altera opacidade/cor.
Offsets e spread aceitam valores negativos; blur exige valor não negativo.
`half_up` aproxima (empate para longe de zero), `floor` vai para menos infinito,
`ceil` para mais infinito. Aritmética Decimal, contexto de 40 dígitos.

A cor de entrada pode ser `#RRGGBB`, objeto DTCG color sRGB ou alias de cor
existente. Alpha final = alpha da cor × opacity (ambos 0–1), arredondado com
ROUND_HALF_UP em `opacity_precision` casas (0–8). Não há clamp silencioso.
Opacity não é um campo próprio de shadow DTCG: o resultado vai no alpha da cor
derivada, sem modificar Colors. Revise quando arredondamento gerar alpha zero.

```bash
python3 /caminho/da/skill/scripts/elevation.py --plan /tmp/elevation-plan.json
python3 /caminho/da/skill/scripts/elevation.py --plan /tmp/elevation-plan.json --existing /projeto/tokens.json
```

Guarde o plano fora do consumidor antes de aprovação. O helper apenas imprime
JSON; não tem modo de escrita. Exit 0 significa parâmetros/aliases validados,
não aprovação visual ou portabilidade total; erros retornam 1 sem preview parcial.
Reutiliza utilitários dos scripts vizinhos spacing/borders/colors, sem executar
suas operações ou exigir leitura de suas referências.

A saída resumida traz `token_changes` com os valores anteriores e propostos;
use `--full` para incluir o documento completo em `tokens`.

## Tokens e reuso

Primitivos `primitive.elevation.shadow.<nível>` usam `$type: shadow`, com lista de
camadas na ordem CSS/DTCG (frente para trás). Cada camada contém color, offsetX,
offsetY, blur, spread e inset; color pode ser alias e dimensões são px/rem.
`primitive.elevation.color.<nível>.layer<N>` contém apenas cores necessárias à
sombra; semânticos `semantic.elevation.<finalidade>` usam aliases de shadow.
`semantics` aceita nomes simples legados (`card`), caminhos relativos pontuados
(`surface.raised`) e grupos aninhados (`{"surface": {"raised": "{primitive.elevation.shadow.low}"}}`).
Os dois formatos hierárquicos emitem `semantic.elevation.surface.raised`; cada
folha deve ser alias de shadow. Não inclua o prefixo `semantic.elevation` na chave.
Segmentos vazios/reservados, grupos vazios, caminhos repetidos após normalização
e colisões entre token e grupo são recusados; não há renomeação de tokens existentes.
Aliases para outros semânticos precisam de alvo existente ou emitido anteriormente,
como no formato legado. Preview, reuso e projeções usam os caminhos completos.

Nenhum nível ou receita é criado implicitamente. `none: []` expressa ausência,
projetada como box-shadow none e lista Flutter vazia, sem sombra transparente fictícia.

Níveis podem ser aliases de shadows existentes. Camadas individuais também podem
ser aliases, mas precisam resolver um objeto único: arrays não são achatados.
`levels: {}` permite apenas reutilizar sombras nas finalidades semânticas.
Resolve tipos herdados e aliases de componentes color/dimension em shadows
existentes. Não resolve $extends/JSON Pointer ou cores fora de sRGB; hex legado
em um token color DTCG exige mapeamento explícito em cópia temporária.

Valores iguais reutilizam aliases dentro de Elevation, sem acoplar dimensões de
outras fundações por coincidência. Cores originais são reutilizadas quando o alpha
final coincide; cores derivadas permanecem separadas. Preserve metadados e decisões.
Colisões, ciclos, tipos incompatíveis e níveis sem finalidade são recusados.
Primitivos intermediários criados pelo helper e dispensados pela deduplicação são
removidos do preview; tokens recebidos em --existing nunca são removidos.
Não sobrescreva arquivo parcial com documento combinado de múltiplos arquivos.

## CSS e Flutter

A saída inclui níveis resolvidos, projeções e avisos. CSS mantém a ordem das
camadas; Flutter BoxDecoration pinta sua lista de trás para frente, portanto a
projeção BoxShadow inverte a lista para preservar sobreposição. Insets continuam
válidos no CSS/DTCG, mas bloqueiam a projeção Flutter inteira (`supported: false`,
`boxShadow: null`) por falta de equivalente direto; não os descarte ou transforme
silenciosamente. Uma adaptação exige proposta e aprovação separadas.

A projeção usa os mesmos números de blur, offset e spread em pixels lógicos,
com conversão rem × root_px explícita e sem DPR. Não garante equivalência visual:
CSS aproxima Gaussian sigma blur/2; Flutter converte radius positivo em sigma
por `radius × 0.57735 + 0.5` (zero permanece zero). O diagnóstico calculado é
informativo, baseado na implementação consultada, não uma conversão universal.
Não troque blurRadius por sigma ao instanciar BoxShadow. Não há geração de Dart.

Spread negativo pode contrair até desaparecer conforme a geometria; clipping,
formas, cantos, blur, sombras inset e renderizadores precisam de inspeção real.
Várias sombras/blur extenso podem aumentar custo: revise o mínimo necessário por
finalidade, sem presumir um orçamento. Sombra não altera layout nem substitui
contraste, borda, foco ou tamanho de alvo. Em temas escuros, confirme a estratégia
visual existente; não invente overlays ou cores para substituir sombras.

## Aprovação e persistência

Apresente tabela de níveis/camadas, valores finais, alpha efetivo, usos, aliases,
limitações e resultados da validação. Destaque inset sem suporte Flutter, alpha
zero e diferenças de blur; cálculos válidos não provam ausência de excessos ou
conformidade visual/acessível. Mostre caminhos e diff de tokens/decisões, sem
mudanças em Colors, Typography, Spacing ou Borders. Aguarde aprovação explícita;
reapresente se a proposta mudar.

Após aprovação, persista somente o aprovado e acrescente `foundations.elevation`
ao registro existente. Registre plano, fontes, justificativas, usos, caminhos,
arredondamento, composição de alpha, reuso, mapeamento de plataforma, verificações
e pendências. Releia arquivos, resolva aliases, recalcule e confira o diff das
fundações anteriores. Diferencie preview, persistência e validação visual real.

Fontes: [DTCG Shadow](https://www.designtokens.org/tr/2025.10/format/#shadow),
[CSS Shadows](https://www.w3.org/TR/css-backgrounds-3/#box-shadow),
[Flutter BoxShadow](https://api.flutter.dev/flutter/painting/BoxShadow-class.html),
[conversão sigma](https://api.flutter.dev/flutter/dart-ui/Shadow/convertRadiusToSigma.html),
[ordem de pintura Flutter](https://github.com/flutter/flutter/blob/master/packages/flutter/lib/src/painting/box_decoration.dart).
