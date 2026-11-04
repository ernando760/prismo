# Resultados Elevation — 2026-11-02

Fixture matemática, sem aprovação de identidade ou valores para nenhum consumidor.
Cálculos executados em preview; nenhum acesso ou alteração ao POC nesta verificação.

## Valores calculados

Unidade px, arredondamento half_up a 0.25px e alpha com quatro casas decimais.
Todos os níveis e receitas são entradas da fixture, sem presets embutidos.

| Nível | Offset X/Y | Blur | Spread | Alpha final | Finalidade de teste |
| --- | --- | --- | --- | --- | --- |
| none | — | — | — | — | flat: ausência de sombra |
| low | 0/1px | 2px | 0px | 0.12 | card |
| medium | 0/2px | 4px | -0.5px | 0.16 | popover |
| high | 0/6px | 12px | 0px | 0.2 | dialog |

High usa scale 2 sobre offsetY 3 e blur 6; a opacidade 0.2 não é multiplicada
por scale. Composição de alpha testada separadamente: 0.5 × 0.24 = 0.12.

## Tokens e projeções

- Primitivos shadow: `primitive.elevation.shadow.<nível>`.
- Cores de sombra: `primitive.elevation.color.<nível>.layer<N>`.
- Semânticos shadow por aliases: `semantic.elevation.<finalidade>`.
- None é shadow com lista vazia: CSS none e lista Flutter vazia.
- Dimensões DTCG px/rem; opacidade final é alpha em color, não campo adicional de shadow.

CSS calculado para low:

```css
box-shadow: 0.0px 1.0px 2.0px 0.0px rgb(0.0 0.0 0.0 / 0.12);
```

Flutter low: offset [0, 1], blurRadius 2, spreadRadius 0, alpha 0.12.
Listas são invertidas na projeção Flutter para preservar a sobreposição CSS.
Com unidade rem e raiz explícita de 16px, blur 2rem projetou blurRadius 32.

Inset foi executado como cenário adicional: CSS gerado, Flutter supported false
e boxShadow null, com aviso; nenhuma camada descartada silenciosamente.

O diagnóstico de Flutter para blurRadius 4 é sigma 2.8094, enquanto a referência
CSS para blur 4 aproxima sigma 2. Não foi feita conversão para equivalência visual;
blurRadius continua recebendo raio, não sigma.

## Verificações executadas

```bash
python3 skills/prismo/scripts/elevation.py --plan tests/fixtures/elevation-plan.json
python3 -m unittest discover -s tests -q
```

Resultado: 107 testes aprovados, incluindo 20 de Elevation.

- Cálculos com scale, parâmetros assinados, arredondamento decimal e composição de alpha.
- Blur negativo, opacidade/alpha fora de 0–1, valores não finitos e tipos inválidos recusados.
- Shadows multicamada, aliases de componentes, ausência, inset e projeções rem.
- Alias de camada resolvendo array é recusado; arrays não são achatados.
- Preservação de cores de origem, metadados, reexecução e deduplicação.
- Remoção apenas de cores intermediárias novas que ficaram sem uso após deduplicar.
- Colisões, ciclos, aliases ausentes e níveis sem finalidade recusados.
- Integração CLI Colors → Typography → Spacing → Borders → Elevation em diretório temporário.
- Subárvores anteriores preservadas no preview; bytes de tokens e decisões permanecem intactos.
- Sintaxe Bash e validador estrutural da skill executados.

## Limitações

Valida o subconjunto de parâmetros, tipos e aliases suportado, não todo DTCG,
performance, contraste ou layout. Não renderiza sombras, não mede se são excessivas,
não gera Dart e não converte elevação Material em shadow. Usa só cores sRGB, sem
$extends/JSON Pointer. Clipping, shapes, blur, spread e temas precisam de revisão
real antes da adoção. Persistência no consumidor exige aprovação dos valores e diff.

Fontes: [DTCG Shadow](https://www.designtokens.org/tr/2025.10/format/#shadow),
[CSS Shadows](https://www.w3.org/TR/css-backgrounds-3/#box-shadow),
[Flutter BoxShadow](https://api.flutter.dev/flutter/painting/BoxShadow-class.html),
[convertRadiusToSigma](https://api.flutter.dev/flutter/dart-ui/Shadow/convertRadiusToSigma.html).
