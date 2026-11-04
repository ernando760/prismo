# foundations — Borders

## Investigar e esclarecer

Leia `design-system/decisions.json` (ou caminho documentado) e os tokens indicados.
Sem registro, informe a ausência e proponha `init`, sem inicializar silenciosamente.
Preserve integralmente Colors, Typography, Spacing e suas decisões. Carregue só
esta referência; o helper reutiliza cálculos utilitários, sem executar Spacing.

Busque raios e espessuras recorrentes em tokens, CSS, temas e BorderRadius,
BorderSide e ShapeBorder do Flutter. Leia amostras representativas e registre
fontes; valores isolados não provam uma escala. Reutilize nomes, escalas e usos
existentes. Não converta tokens legados nem acrescente cores ou estilos de traço.

Pergunte só pelas lacunas, agrupadas: aparência reta/arredondada/full; bases,
passos e arredondamento de raio e espessura; usos reais (controles, cards,
divisores etc.); plataformas e raiz de conversão se rem. Confirme como borda
ausente e hairline são usadas, pois zero tem comportamento diferente em Flutter.
Para full, confirme cápsula/círculo dependente da geometria; não presuma 9999px.
Não repita respostas, invente uma identidade ou crie passos sem finalidade.

## Calcular preview

Execute `scripts/borders.py` com Python 3.9+ e biblioteca padrão. O helper depende
do arquivo vizinho `spacing.py`, instalado junto à skill. Plano ilustrativo:

```json
{
  "radius": {
    "base": {"value": 4, "unit": "px"},
    "steps": {"none": 0, "control": 1},
    "rounding": {"mode": "half_up", "increment": 1}
  },
  "width": {
    "base": {"value": 1, "unit": "px"},
    "steps": {"thin": 1},
    "rounding": {"mode": "half_up", "increment": 0.5}
  },
  "full": true,
  "bounds_px": {"width": 120, "height": 40},
  "root_px": null,
  "semantics": {
    "radius": {"square": "{primitive.borders.radius.none}", "control": "{primitive.borders.radius.control}", "pill": "{primitive.borders.radius.full}"},
    "width": {"divider": "{primitive.borders.width.thin}"}
  }
}
```

Para cada escala, `valor = base × multiplicador`. Multiplicadores explícitos
podem ser sequenciais ou personalizados/fracionários. Base positiva, dimensões e
multiplicadores não negativos. Arredondamento decimal para múltiplos do incremento
na unidade da base, com `half_up` (empate para cima), `floor` ou `ceil`, contexto
de 40 dígitos. Apresente o bruto e final, sobretudo quando arredondar para zero.

```bash
python3 /caminho/da/skill/scripts/borders.py --plan /tmp/borders-plan.json
python3 /caminho/da/skill/scripts/borders.py --plan /tmp/borders-plan.json --existing /projeto/tokens.json
```

Guarde o plano fora do consumidor até aprovação. A saída é somente stdout;
exit 0 significa cálculo/validação do subconjunto suportado, não aprovação visual.
Erros retornam 1 sem preview parcial. Não há modo de escrita.

A saída resumida traz `token_changes` com os valores anteriores e propostos;
use `--full` para incluir o documento completo em `tokens`.

## Tokens e plataformas

Primitivos: `primitive.borders.radius.<passo>` e
`primitive.borders.width.<passo>`. Semânticos:
`semantic.borders.<radius|width>.<uso>`, exclusivamente por aliases `{caminho}`.
Raio/espessura usam `$type: dimension` com value/unit px ou rem. São tipos DTCG
existentes; não há tipos borderRadius/borderWidth. Borda reta é raio zero.

`full: true` gera `primitive.borders.radius.full` com `$type: number`, `$value: 0.5`.
Essa é uma convenção Prismo: fração do menor lado para calcular raio circular
uniforme, não uma unidade ou forma nativa DTCG. O semântico full também usa number
por alias. Não exporte `full`, `%`, infinito ou 9999 como dimensão e não interprete
0.5 como 0.5px. A integração consumidora precisa aplicar a regra registrada.

Para CSS full, o preview indica estratégia runtime `min(width,height)/2`. Com
`bounds_px` reais, calcula um exemplo numérico; com null, deixa o raio CSS pendente
de geometria. Recalcular ao redimensionar, usando dimensões atuais do border-box.
No Flutter, mapeie a intenção a StadiumBorder, ou a raio calculado no layout.
Uma caixa 120×40 ou 40×120 produz raio 20; 40×40 produz círculo. Não substitua por
50% em um retângulo: isso pode produzir elipse, em vez de cápsula com pontas circulares.
`bounds_px` não é limite universal e seu raio não vira token fixo para todos os usos.

Dimensões finitas têm projeção CSS e pixels lógicos Flutter. Rem exige root_px
explícito, inclusive em aliases; é referência de conversão, sem impor raiz CSS.
Não multiplique por DPR. Espessura zero significa borda ausente neste fluxo:
o preview Flutter indica `style: none`, porque BorderSide(width: 0) sozinho é
hairline. Se o projeto deseja hairline, registre a pendência e proponha mapeamento
contextual separado, sem confundi-lo com ausência. Espessuras positivas não
escolhem cor ou estilo; reutilize os existentes. O helper não monta composite
DTCG border incompleto nem implementa componentes, clipping ou animação.

## Reutilizar, aprovar e registrar

Passos podem ser aliases para dimensões existentes, preservadas sem arredondar;
`steps: {}` permite só reutilizar escalas. `full: false` não apaga nada e permite
referenciar um full existente. O helper resolve aliases e tipos herdados, recusa
conflitos, ciclos, valores negativos e tipos incompatíveis. Reuso automático de
valores iguais limita-se aos primitivos de Borders ou fontes explicitamente
indicadas; não acople outras fundações por coincidência numérica. Valores iguais
em raios/espessuras podem compartilhar literais via alias. Cada passo declarado
precisa participar do grafo de aliases de um uso semântico; remova passos sem uso.

`--existing` preserva metadados e tokens alheios. Não resolve $extends/JSON Pointer;
legados CSS/Dart exigem mapeamento revisado em cópia temporária. Não sobrescreva um
arquivo parcial com documento combinado de vários arquivos. A validação não cobre
o DTCG inteiro, layout ou acessibilidade. Raio não comprova tamanho de alvo e
espessura isolada não comprova contraste; não recalcule Colors nesta operação.

Apresente bases, passos, justificativas, bruto/final, aliases, usos, regra full,
projeções, pendências e diff de caminhos/tokens/decisões antes de gravar. Aguarde
aprovação explícita; mudanças na proposta exigem nova aprovação. O pedido genérico
de Borders não aprova valores ainda desconhecidos.

Após aprovação, persista só o aprovado e acrescente `foundations.borders` ao registro,
preservando todas as seções anteriores. Registre plano, evidências, justificativas,
caminhos, reuso, arredondamento, interpretação de full/zero, conversão e limitações.
Releia tokens finais, resolva aliases, recalcule com o plano aprovado e confira o
diff das outras fundações. Relate verificações executadas e diferencie preview,
persistência e validação visual. Não declare conformidade por cálculo apenas.

Fontes: [DTCG](https://www.designtokens.org/tr/2025.10/format/),
[CSS cantos](https://www.w3.org/TR/css-backgrounds-3/#corner-overlap),
[StadiumBorder](https://api.flutter.dev/flutter/painting/StadiumBorder-class.html),
[BorderSide.width](https://api.flutter.dev/flutter/painting/BorderSide/width.html).
