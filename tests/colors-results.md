# Resultados Colors — 2026-11-02

Demonstração técnica; cores não aprovadas como identidade de nenhum projeto.

## Escala de teste

Seed `#ff0000`; luminosidades explícitas, chroma e matiz derivados da seed.
Redução de chroma por 48 iterações; exportação sRGB de 8 bits.

| Passo | Hex final | L solicitado | C final antes da quantização | H | Gama ajustada |
| --- | --- | --- | --- | --- | --- |
| primitive.sample.100 | `#ffe9e5` | 0.95 | 0.02499651 | 29.23389 | True |
| primitive.sample.300 | `#ffa193` | 0.80 | 0.11478155 | 29.23389 | True |
| primitive.sample.500 | `#f00000` | 0.60 | 0.24621170 | 29.23389 | True |
| primitive.sample.700 | `#8b0000` | 0.40 | 0.16414113 | 29.23389 | True |
| primitive.sample.900 | `#320000` | 0.20 | 0.08207057 | 29.23389 | True |

## Contraste

| Par | Razão | Uso | AA | AAA |
| --- | --- | --- | --- | --- |
| `#000000` / `#ffffff` | 21.000000000000 | normal_text | True | True |
| `#777777` / `#ffffff` | 4.478089453577 | normal_text | False | False |
| `#ff0000` / `#ffffff` | 3.998476770754 | normal_text | False | False |
| `#ff0000` / `#ffffff` | 3.998476770754 | large_text | True | False |
| `#ff0000` / `#ffffff` | 3.998476770754 | non_text | True | N/A |
| Escala sample 900 / 100 | 15.884682588177 | normal_text | True | True |

Aprovação usa a razão completa, sem arredondamento. A tabela mostra 12 casas.
AAA não se aplica ao cálculo de contraste não textual (1.4.11).

## Verificação executada

- Vetor conhecido OKLCH do vermelho sRGB e round-trip de 64 cores.
- Varredura de 120 combinações L/H fora da gama, preservando L/H e reduzindo C.
- Preto/branco, cores idênticas, luminância e limiares AA/AAA, incluindo valores imediatamente abaixo.
- Aliases DTCG, claro/escuro, reutilização, colisões, entradas inválidas e preview sem escrita.

Comando: `python3 -m unittest discover -s tests -v` — 38 testes aprovados (15 Colors).

Preview reproduzível: `python3 skills/prismo/scripts/colors.py palette --plan tests/fixtures/colors-plan.json`.
Scripts também executados via CLI com preto/branco (aprovação) e cinza/branco
(falha AA com código 2). O helper não lê nem altera o POC nesta verificação.

Os testes cobrem os cálculos e a geração suportada, não conformidade WCAG completa
nem validação de todos os recursos da especificação DTCG.

Fontes: [WCAG 2.2](https://www.w3.org/TR/WCAG22/),
[CSS Color 4](https://www.w3.org/TR/css-color-4/#ok-lab),
[DTCG](https://www.designtokens.org/tr/2025.10/format/#color).
