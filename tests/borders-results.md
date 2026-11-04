# Resultados Borders — 2026-11-02

Fixture matemática, sem aprovação dos valores para nenhum projeto consumidor.
Scripts executados via CLI em preview; nenhum arquivo do POC foi acessado ou alterado.

## Escalas

Radius: base 4px, multiplicadores 0/1/2, arredondamento half_up a 1px.
Width: base 1px, multiplicadores 0/1/2, arredondamento half_up a 0.5px.

| Token primitivo | Tipo | Valor final |
| --- | --- | --- |
| primitive.borders.radius.none | dimension | 0.0px |
| primitive.borders.radius.sm | dimension | 4.0px |
| primitive.borders.radius.md | dimension | 8.0px |
| primitive.borders.radius.full | number | 0.5 × menor lado |
| primitive.borders.width.none | dimension | 0.0px |
| primitive.borders.width.thin | dimension | 1.0px |
| primitive.borders.width.strong | dimension | 2.0px |

## Usos e aliases

| Uso | Alias |
| --- | --- |
| semantic.borders.radius.square | `{primitive.borders.radius.none}` |
| semantic.borders.radius.control | `{primitive.borders.radius.sm}` |
| semantic.borders.radius.card | `{primitive.borders.radius.md}` |
| semantic.borders.radius.pill | `{primitive.borders.radius.full}` |
| semantic.borders.width.absent | `{primitive.borders.width.none}` |
| semantic.borders.width.divider | `{primitive.borders.width.thin}` |
| semantic.borders.width.emphasis | `{primitive.borders.width.strong}` |

O zero de width é alias do zero de radius. Valores iguais usam aliases dentro
de Borders; não há acoplamento automático aos valores das outras fundações.

## Full e diferenças de plataforma

- Full é um token DTCG number 0.5, com convenção Prismo: metade do menor lado.
- Caixas 120×40 e 40×120 → raio 20px; caixa 40×40 → círculo de raio 20px.
- Preview CSS com bounds 120×40: `20.0px`.
- Sem bounds, borderRadius é `None`; a regra runtime permanece min(width,height)/2.
- Flutter full projeta StadiumBorder, cuja forma depende do retângulo atual.
- Espessura zero projeta style none em Flutter; width zero sozinho seria hairline.
- Raio finito rem requer raiz explícita: base 0.25rem × 16 → raio 4 pixels lógicos.
- Valor confirmado por CLI: `4.0` pixels lógicos.

Essas projeções não geram CSS/Dart ou componentes. O valor 0.5 não é um raio
0.5px nem uma porcentagem diretamente exportável. Não foi feita validação visual.

## Verificação

Comandos reproduzíveis:

```bash
python3 skills/prismo/scripts/borders.py --plan tests/fixtures/borders-plan.json
python3 -m unittest discover -s tests -v
```

Resultado: 87 testes aprovados, sendo 16 de Borders.

- Vetores de raios/espessuras, frações e arredondamento half_up/floor/ceil.
- Full horizontal/vertical/quadrado, com e sem dimensões conhecidas.
- Dimensões, multiplicador full e aliases tipados resolvidos.
- Preservação de metadados, determinismo, reexecução e reuso sem duplicação.
- Colisões, ciclos, tipos incompatíveis, passos sem uso e parâmetros inválidos recusados.
- Conversão rem e ausência de dependência automática com Spacing/Typography.
- Integração real de CLI em diretório temporário: Colors → Typography → Spacing → Borders.
- Subárvores das três fundações preservadas no preview; bytes de tokens e decisões intactos.

Sintaxe Bash e validador estrutural de skills também executados.

Limites: subconjunto DTCG suportado, sem $extends/JSON Pointer; full exige um
adaptador de plataforma. Não valida layout, clipping, contraste, acessibilidade,
cores de borda ou estilos de traço. Não suporta hairline como ausência de borda.
Aprovação e persistência em um consumidor real não foram exercitadas nestes testes.

Fontes: [DTCG](https://www.designtokens.org/tr/2025.10/format/),
[CSS cantos](https://www.w3.org/TR/css-backgrounds-3/#corner-overlap),
[StadiumBorder](https://api.flutter.dev/flutter/painting/StadiumBorder-class.html),
[BorderSide.width](https://api.flutter.dev/flutter/painting/BorderSide/width.html).
