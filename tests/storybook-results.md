# Storybook — validação inicial, 2026-11-02

> Registro histórico da etapa: contagens, bloqueios e pendências abaixo descrevem
> aquela execução. Para o estado de preparação atual, consulte o
> [checklist da release experimental](../docs/experimental-release-checklist.md).

## Implementado

- Inspeção somente leitura de Web declarado, evidências e configuração Storybook.
- Cinco stories CSF; renderer HTML e adaptador React; sem componentes de produção.
- Visualizações Colors, Typography, Spacing, Borders e Elevation.
- Comparação light/dark e filtro por nome, sem valores de tokens transcritos.
- Fonte import JSON DTCG; configuração de caminhos e fallback tipográfico opcional.

## Executado

- Python: 115 testes aprovados, incluindo 8 de inspeção Storybook.
- Node: 13 testes de resolução/modelos/exportação aprovados.
- DOM simulado com jsdom já disponível: 8 testes aprovados (nenhuma instalação).
- Testes DOM cobrem cinco fundações, comparação/troca de tema, filtro, vazios,
  propagação de tamanho/fallback, full, espessura zero, erros e ausência de injeção HTML.
- node --check executado nos templates de stories e renderer.
- Sintaxe Bash e quick_validate.py da skill executados.
- Detector mecânico Impeccable executado: nenhuma ocorrência reportada.

Total: 136 testes aprovados. DOM simulado não comprova layout ou aparência.

## Leitura do POC

Projeto: `/home/ernandomfr/Documentos/Projects/prismo-poc`.
Web está declarado, mas não há manifesto Web nem Storybook configurado.
A decisão Storybook planejado não foi tratada como aprovação para instalação.
Nenhuma instalação/configuração ou arquivo novo foi criado no POC.
Hashes SHA-256 de tokens.json e decisions.json permaneceram iguais antes/depois.

Os modelos foram calculados diretamente com a fonte DTCG real em leitura:

| Coleção | Claro | Escuro |
| --- | --- | --- |
| colors | 31 | 31 |
| typography | 3 | 3 |
| spacing | 6 | 6 |
| radius | 7 | 7 |
| width | 3 | 3 |
| elevation | 4 | 4 |

Nenhum erro de resolução. Renderer DOM com essa fonte: dois painéis, 12 coleções
(radius e width são duas coleções de Borders), 108 amostras e nenhum aviso.
Fallback adicional mapeado ao token existente primitive.typography.family.webFallback.

A cópia em /tmp usada nos testes é descartável, não uma fonte mantida para stories.
Na integração real, a story deve importar o arquivo original, no caminho aprovado.

## Bloqueios e limites

- A consulta ao registry npm falhou por DNS: EAI_AGAIN registry.npmjs.org.
- Tentativa de servidor HTTP local falhou com PermissionError ao criar socket.
- O host de navegador da ferramenta de UI estava indisponível.
- Build real do Storybook, HMR, execução dos adapters no renderer Storybook,
  screenshots e revisão visual/responsiva **não foram executados/aprovados**.
- O suporte inicial pronto cobre HTML/React; outros renderers requerem adaptação.
- O resolver não implementa toda a especificação DTCG nem modos Resolver.

Integração no consumidor precisa de aprovação do framework/dependências/configuração
quando ausente e execução do build/browser em um ambiente com esses recursos.

## Reprodução

```bash
python3 -m unittest discover -s tests -q
node tests/storybook/catalog.test.mjs
node --check skills/prismo/assets/storybook/catalog.mjs
# Opcional, com jsdom disponível no ambiente de testes:
PRISMO_JSDOM_PATH=/caminho/para/jsdom node tests/storybook/render.test.mjs
```

Sem jsdom, o arquivo render.test.mjs declara seus oito testes como ignorados;
eles não devem ser contados como aprovados nesse ambiente. Não é dependência
de produção. tests/storybook/preview.html permite validar o renderer num servidor
local copiando os módulos para o mesmo diretório e usando tokens de teste como
tokens.json; não é um substituto de validação no Storybook.

Fontes: [CSF](https://storybook.js.org/docs/api/csf),
[Args](https://storybook.js.org/docs/writing-stories/args),
[Instalação](https://storybook.js.org/docs/get-started/install/).
