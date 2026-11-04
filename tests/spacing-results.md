# Resultados Spacing — 2026-11-02

Fixture matemática; estes valores não são decisões aprovadas de identidade/layout.
O helper foi executado via CLI em preview; nenhum arquivo do consumidor foi escrito.

## Escala linear

Base 4px; start 0; increment 1; arredondamento half_up para múltiplos de 1px.
Fórmula: `4 × (0 + 1 × índice)`.

| Passo | Índice | Bruto | Final CSS | Flutter lógico |
| --- | --- | --- | --- | --- |
| none | 0 | 0px | 0.0px | 0 |
| xs | 1 | 4px | 4.0px | 4 |
| sm | 2 | 8px | 8.0px | 8 |
| md | 3 | 12px | 12.0px | 12 |
| lg | 4 | 16px | 16.0px | 16 |
| xl | 6 | 24px | 24.0px | 24 |

## Usos semânticos

| Uso | Alias | Dimensão final |
| --- | --- | --- |
| semantic.spacing.gap.compact | `{primitive.spacing.sm}` | 8.0px |
| semantic.spacing.padding.container | `{primitive.spacing.lg}` | 16.0px |
| semantic.spacing.margin.section | `{primitive.spacing.xl}` | 24.0px |

## Escala personalizada e rem

Base 4px e multiplicadores personalizados 0, 0.5, 1.5, 2, 5, 7.5:
`0.0px, 2.0px, 6.0px, 8.0px, 20.0px, 30.0px`.

Escala linear repetida com base 0.25rem, incremento de arredondamento 0.0001rem
e raiz explícita de conversão 16px:

| Passo | Dimensão CSS | Flutter lógico |
| --- | --- | --- |
| none | 0.0rem | 0 |
| xs | 0.25rem | 4 |
| sm | 0.5rem | 8 |
| md | 0.75rem | 12 |
| lg | 1.0rem | 16 |
| xl | 1.5rem | 24 |

Arredondamento de 6px para grade de 4px: half_up → 8px; floor → 4px; ceil → 8px.
Passos colapsados pelo arredondamento são aliases, inclusive quando viram zero.

## Verificações executadas

- Valores conhecidos de escalas linear/personalizada e início/incremento fracionários.
- Arredondamento decimal, empates e modos half_up/floor/ceil.
- Dimensões DTCG e aliases gap/padding/margin resolvidos e tipados.
- Reuso explícito de legados, preservação de metadados e reexecução sem duplicação.
- Colisões, tipos/aliases inválidos, ciclos e dimensões negativas recusados.
- CSS preserva a precisão numérica exportada e rem exige raiz explícita.
- Integração CLI Colors → Typography → Spacing em diretório temporário:
  tokens anteriores preservados no preview; bytes de tokens e decisões não alterados.
- Nenhuma dependência automática de spacing em tamanhos de fonte iguais.

Comandos reproduzíveis:

```bash
python3 skills/prismo/scripts/spacing.py --plan tests/fixtures/spacing-plan.json
python3 -m unittest discover -s tests -v
```

Resultado: 71 testes aprovados, sendo 17 de Spacing. A sintaxe Bash e o validador
estrutural de skills também foram executados.

Limites: validação do subconjunto de dimensões/aliases suportado; não é validador
DTCG completo, teste de layout, acessibilidade ou equivalência visual Web/Flutter.
Valores negativos, unidades contextuais e $extends/JSON Pointer não são suportados.
A raiz rem é uma referência informada e a conversão não usa DPR.
Aprovação e persistência no consumidor não foram exercitadas por estes testes.
Nenhum arquivo do POC foi alterado.

Fontes: [DTCG Dimension](https://www.designtokens.org/tr/2025.10/format/#dimension)
e [Flutter EdgeInsets](https://api.flutter.dev/flutter/painting/EdgeInsets-class.html).
