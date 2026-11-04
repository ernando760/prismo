# foundations — Colors

## Investigar e esclarecer

1. Leia `design-system/decisions.json` antes de propor cores. Se o projeto tiver
   documentado outro caminho, use-o. Se não houver registro, informe a ausência e
   proponha executar `init`; não invente decisões nem inicialize silenciosamente.
2. Use o registro e buscas direcionadas para localizar tokens, temas CSS/Dart,
   estilos, marca e decisões já fornecidas. Inspecione apenas os arquivos relevantes,
   excluindo dependências e a própria skill. Reutilize cores, nomes e papéis existentes;
   não crie outra fonte de verdade. Identifique o formato dos tokens encontrados.
3. Pergunte só pelas lacunas, agrupadas: cores oficiais e fonte da marca; preferências
   visuais/restrições; suporte a claro, escuro ou ambos. A existência de um tema não
   autoriza inventar outro. Confirme também papéis semânticos e pares de uso ainda
   indefinidos. Respostas anteriores e tokens existentes prevalecem.
4. Proponha seeds, luminosidades da escala e mapeamentos de papéis. A ferramenta
   não escolhe identidade, número de passos, tema ou cor de texto automaticamente.
   Sem autorização para explorar uma identidade, espere as respostas. Não implemente
   tipografia, espaçamento, componentes nem outras fundações.

## Calcular em preview

Use `scripts/colors.py` (Python 3.9+, biblioteca padrão), relativo à pasta da skill.
O plano contém somente escolhas explícitas ou propostas identificadas como tais:

```json
{
  "palettes": {
    "brand": {"seed": "#336699", "steps": {"100": 0.95, "500": 0.6, "900": 0.25}}
  },
  "themes": {"light": {"text": "primitive.brand.900", "surface": "primitive.brand.100"}},
  "pairs": [{"foreground": "semantic.light.text", "background": "semantic.light.surface", "usage": "normal_text"}]
}
```

Exemplo ilustrativo, não recomendação de marca. Guarde o plano fora do projeto
consumidor enquanto não houver aprovação. Seeds aceitam `#RRGGBB` ou `[L,C,H]`
OKLCH (`L: 0–1`, `C: 0–1`, `H: 0–360`). Seeds hex preservam matiz e chroma ao
variar L; o valor original não é automaticamente incluído ou substituído. Caso
necessário, reutilize o token original como referência semântica para a marca.

```bash
python3 /caminho/da/skill/scripts/colors.py palette --plan /tmp/colors-plan.json
# Para reutilizar o documento DTCG existente sem o alterar:
python3 /caminho/da/skill/scripts/colors.py palette --plan /tmp/colors-plan.json --existing /projeto/tokens.json
python3 /caminho/da/skill/scripts/colors.py contrast '#777777' '#ffffff' --usage normal_text --fail-on AA
```

A saída vai exclusivamente para stdout; não há modo de persistência. Em `palette`,
saída zero significa cálculo concluído, não contraste aprovado: confira cada par.
Em `contrast`, `--fail-on AA|AAA` retorna 2 se o critério falhar ou não se aplicar;
entradas inválidas retornam 1. Sem essa opção o resultado é apenas informativo.

O resultado resumido contém `token_changes`, `swatches`, `reused` e `contrast`;
use `palette --full` para incluir o documento completo em `tokens`. Os tokens novos
ficam em `primitive.<paleta>.<passo>` e os semânticos em
`semantic.<light|dark>.<papel>`, com aliases DTCG. Temas são grupos nomeados deste
projeto, não uma extensão de modos padronizada pelo DTCG. Não renomeie tokens
existentes só para adaptar a essa convenção: podem ser usados como alvo dos papéis.
`palettes: {}` permite apenas reutilizar cores existentes. Para um nome semântico
existente, reutilize-o nos pares, sem gerar um novo papel redundante; use, por exemplo, `themes: {"light": {}}` quando todos os papéis já existirem.

`--existing` recebe um documento combinado com os nomes/aliases originais. O
preview preserva os tokens alheios e recusa colisões com valores diferentes.
Valores de cor idênticos reutilizam aliases em vez de repetir literais. Não grave
um documento combinado por cima de um arquivo parcial em projetos com vários
arquivos. Nesses projetos, apresente o diff dos arquivos de origem pertinentes.

O helper resolve cores sRGB opacas e aliases `{caminho}` com tipo `color`, inclusive
herdado de grupo. Outros espaços, transparência, `$extends` e `$ref` exigem adaptação
explícita em cópia temporária ou cálculo apropriado separado. Não migre o original
nem ignore erros para declarar aprovação. Tokens legados CSS/Dart precisam de um
mapeamento revisado: não são interpretados automaticamente como DTCG.

## Algoritmo e limites

- Conversão sRGB linear ↔ OKLab ↔ OKLCH. Cada passo usa o L informado e C/H da seed.
- Fora de sRGB: reduzir C por busca binária de 48 iterações, mantendo L/H. Em
  L=0/1, usar preto/branco; clamp de canais apenas para erro numérico de fronteira.
  Este é um método simples de redução de chroma, não o algoritmo CSS local-MINDE.
- Exportar cores sRGB opacas quantizadas em 8 bits, em objetos DTCG com
  `colorSpace`, `components`, `alpha` e `hex`. `requested_oklch`, `mapped_oklch` e
  o indicador de gamut mapping ficam no relatório, fora dos tokens. A quantização
  pode alterar ligeiramente L/H; contraste é calculado após essa etapa, com os
  componentes exatos exportados. Não trocar o token por valores OKLCH no momento
  da persistência sem recalcular o contraste da representação final.
- Contraste WCAG: luminância relativa sRGB, breakpoint 0.04045 e razão
  `(Lmaior + 0.05)/(Lmenor + 0.05)`, sem arredondar para decidir aprovação.

| Uso | AA | AAA |
| --- | --- | --- |
| Texto normal | 4.5:1 — 1.4.3 | 7:1 — 1.4.6 |
| Texto grande | 3:1 — 1.4.3 | 4.5:1 — 1.4.6 |
| Informação visual de componentes/gráficos | 3:1 — 1.4.11 | Não se aplica a este cálculo |

Texto grande: ao menos 18pt (24 CSS px), ou 14pt em negrito (aprox. 18.67 CSS px).
A escolha de `usage` depende do uso real. Avalie foreground/background de cada
estado e tema aprovado; em elementos não textuais considere cores adjacentes e
as exceções do critério. Logos, itens incidentais e controles inativos exigem
análise contextual. Gradientes, imagens e alpha não são resolvidos por este helper.
Passar uma razão não comprova conformidade completa WCAG; cor não deve ser o único
meio de comunicar informação. Não existe um limiar AAA adicional de 1.4.11.

## Apresentar, aprovar e registrar

Apresente antes de persistir: paleta por passo com amostras/hex e OKLCH, ajustes de
gama, fontes reutilizadas, mapeamento semântico por tema e tabela de todos os pares
com razão, uso e resultados AA/AAA. Mostre falhas sem alterar cores de marca para
ocultá-las. Proponha mudanças de papel/combinação e recalcule quando necessário.
Não rotule a paleta inteira como acessível por alguns pares aprovados.

Mostre também os caminhos e o diff proposto dos tokens e do registro de decisões.
Aguarde aprovação explícita desse resultado antes de criar/alterar arquivos no
consumidor. Se a proposta mudar, reapresente. Para atualizar arquivos existentes,
a aprovação precisa abranger as alterações mostradas; preserve o restante.

Após aprovação, persista somente os tokens aprovados e adicione ao registro, sem
substituir decisões de `init`, uma seção `foundations.colors` com: seeds e fontes,
plano aprovado, temas, reutilizações, caminhos finais, algoritmo/quantização,
pares/resultados, limitações e pendências. Use a estrutura existente; no registro
gerado por `init`, acrescente essa seção ao objeto raiz. Verifique os arquivos
persistidos, resolva aliases e execute novamente os cálculos dos pares finais.
Relate o que efetivamente executou. Se só houve preview, declare isso claramente.

Fontes de cálculo e formato:
[CSS Color 4](https://www.w3.org/TR/css-color-4/#ok-lab),
[DTCG Color](https://www.designtokens.org/tr/2025.10/format/#color),
[WCAG 2.2](https://www.w3.org/TR/WCAG22/).
