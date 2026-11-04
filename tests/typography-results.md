# Resultados Typography — 2026-11-02

Fixture matemática, sem aprovação de identidade para o consumidor. `Example Sans`
é um nome ilustrativo, sem fonte instalada ou renderização visual validada.

## Parâmetros e valores

Base 16px, razão 1.25, quatro casas decimais e ROUND_HALF_UP.
Passos -1, 0 e 2 → 12.8px, 16px e 25px.
Line-height/tracking são entradas explícitas para testar as fórmulas, não padrões
universais de legibilidade. Tracking informado em proporção ao tamanho final.

| Estilo | Passo | Tamanho | Multiplicador | Altura calculada | Tracking | Peso |
| --- | --- | --- | --- | --- | --- | --- |
| heading | large | 25px | 1.2 | 30px | -0.5px | 700 |
| body | base | 16px | 1.5 | 24px | 0px | 400 |
| label | small | 12.8px | 1.25 | 16px | 0.512px | 700 |

Os números projetados para Flutter em base px coincidem com as dimensões da tabela;
`height` permanece multiplicador. Esses campos são projeções, não código Dart.

## Conversão rem

Repetido o cálculo com base 1rem e raiz de conversão explícita de 16px:

| Estilo | Tamanho rem | Tracking rem final | Tamanho lógico Flutter | Tracking lógico Flutter |
| --- | --- | --- | --- | --- |
| heading | 1.5625 | -0.0313 | 25 | -0.5008 |
| body | 1 | 0 | 16 | 0 |
| label | 0.8 | 0.032 | 12.8 | 0.512 |

O heading calcula -0.03125rem e exporta -0.0313rem. Sua projeção usa o valor
exportado: -0.0313 × 16 = -0.5008. Aumentar a precisão reduz essa diferença.
A raiz é uma referência informada de conversão; a raiz real do navegador pode
variar com as preferências do usuário. Não há equivalência garantida de métricas.

## Estrutura e verificações

- Primitivos tipados como fontFamily, fontWeight, dimension e number.
- Composites typography com os cinco campos DTCG e aliases resolvidos/tipados.
- Comparação com vetores aritméticos conhecidos, expoentes negativos e arredondamento.
- Entradas inválidas, alias ausente/circular, conflito de tipo/nome e parâmetros incompletos recusados.
- Reexecução preserva tokens existentes e não duplica seus valores literais.
- Colors gerado pela CLI e passado em --existing; suas subárvores permaneceram iguais.
- Preview pela CLI com px e rem; bytes do arquivo de tokens existente preservados.
- Nenhum acesso ou alteração ao projeto POC durante estas verificações.

Comandos reproduzíveis:

```bash
python3 skills/prismo/scripts/typography.py --plan tests/fixtures/typography-plan.json
python3 -m unittest discover -s tests -v
```

Resultado: 54 testes aprovados, sendo 16 de Typography. A validação estrutural
cobre o subconjunto suportado/emitido, não todo o formato DTCG.

## Limites

Não foram testados renderização, carregamento/licença de fontes, layouts em Web/Flutter,
text scaling, overflow ou conformidade WCAG. Não há geração de CSS/Dart nem
instalação de fontes. Fontes, pesos variáveis e fallbacks precisam de mapeamento
real por plataforma. Aliases JSON Pointer, $extends e composites incompletos não
são suportados pelo helper; px/rem são as unidades exportáveis.

Fontes: [DTCG Typography](https://www.designtokens.org/tr/2025.10/format/#typography),
[Flutter TextStyle](https://api.flutter.dev/flutter/painting/TextStyle-class.html),
[WCAG Text Spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html).
