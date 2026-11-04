# audit — resultados e limitações

> Registro histórico da etapa: contagens, bloqueios e pendências abaixo descrevem
> aquela execução. Para o estado de preparação atual, consulte o
> [checklist da release experimental](../docs/experimental-release-checklist.md).

## Implementação

- Roteador SKILL.md disponibiliza audit e carrega apenas audit.md.
- Fluxo somente leitura para fundações, tokens, componentes, decisões e documentação,
  com checagens determinísticas, revisão de contrato e acessibilidade contextual.
- audit.py reutiliza tokens.validate e colors.contrast/evaluate. Não executa comandos
  do consumidor, carrega JS, instala dependências ou aplica correções.
- Modelo opcional de evidências para pares de contraste, bindings e expectativas de
  API/variantes/estados em implementação, docs e catálogo.
- Achados contêm severidade, certeza, localização/evidência e recomendação.
  O helper diferencia comprovado, risco e manual pendente; mantém checklist geral
  de runtime separado da contagem de achados específicos.
- Busca textual limitada, achados agrupados/capados (100) e registros de pares
  limitados a 10, priorizando falhas/pendências e informando totais/omitidos.

Nenhuma outra operação ou fundação foi alterada. Nenhum arquivo do POC/consumidor
foi modificado. O próprio helper desativa a escrita de bytecode antes dos imports.

## Testes executados

**250 testes aprovados; nenhum ignorado:**

| Suíte | Quantidade |
| --- | ---: |
| Python anterior | 173 |
| Novos testes audit | 24 |
| Modelos DTCG do catálogo | 13 |
| Renderer DOM | 24 |
| Adaptadores HTML/React | 2 |
| Templates document | 14 |

Validador estrutural da Skill: **Skill is valid!**

Fluxos novos exercitados:

- Projeto sem falhas comprovadas mantém saída curta e verificações manuais gerais.
- Contraste real preto/branco (21:1), par igual (1:1), usos normal/grande/não textual
  e comparação sem arredondamento prematuro (4.49999 não passa em 4.5).
- Falha numérica identifica par declarado/limiar, sem alegar automaticamente violação
  de uma interface. Evidência ausente/desatualizada, alpha e cor não resolvida
  permanecem pendentes; nomes de tokens não inventam pares.
- Alias ausente, ciclo, tipo incompatível, JSON duplicado e caminhos entre fontes
  detectados; tipos/formatos fora do suporte são manuais, sem falso defeito.
- Valores equivalentes agrupados como risco de consolidação, não erro semântico.
- Literais Web e alguns construtores Dart têm arquivo/linha e certeza de risco.
  Zeros e usos de bindings nos casos testados não geram indício de literal.
- Imagem sem alt explícito no trecho é risco, inclusive com spread; nenhum nome
  acessível de runtime é presumido.
- Expectativas de estados/variantes são comparadas às três fontes; ausência de
  literal é risco e arquivo não lido é manual, não prova de estado inexistente.
- Binding observado associado a token desconhecido é risco rastreável.
- Fontes divididas, decisões customizadas, limites de busca, symlinks, truncamento,
  esquemas inválidos, cap de relatório e ordenação por severidade cobertos.
- CLI retorna 0 sem comprovados, 2 com comprovados e 1 com entrada inválida.
- Readonly comprovado por snapshot de todos os bytes da fixture: helper copiado
  dentro do consumidor, configs/scripts executáveis presentes, nenhuma execução
  desses comandos nem criação de __pycache__ ou arquivo novo.

## Execuções em leitura no POC

1. Execução inicial: 116 tokens válidos no subconjunto; 44 arquivos textuais lidos,
   3 ignorados, sem truncamento; **zero achados comprovados, 6 riscos e 1 pendência**.
   Riscos: cinco arquivos com candidatos a literais e um grupo de valores equivalentes.
   A pendência foi falta de pares de contraste declarados. Esses riscos não foram
   convertidos em defeitos do POC.
2. Verificação dirigida: binding em src/tokens/TokenTheme.tsx e CSS do Button
   identificam onPrimary versus actionPrimary/brand nos dois temas, para estados
   default/hover/active de filled habilitado. O helper leu src e portal/docs
   (17 arquivos) e calculou seis pares declarados como texto normal:

| Tema / estado | Razão calculada | AA de texto normal |
| --- | ---: | --- |
| Claro / default | 7.271198575988989 | Passa |
| Claro / hover | 10.434001564795818 | Passa |
| Claro / active | 14.76426035596113 | Passa |
| Escuro / default | 8.981832534233202 | Passa |
| Escuro / hover | 12.79819750438452 | Passa |
| Escuro / active | 16.49187661318982 | Passa |

Evidência: Button.css linhas 5–9, associadas aos caminhos em TokenTheme.tsx.
O mesmo seletor default é compartilhado pelos temas; hover/active têm seletores
específicos. A presença dos trechos foi conferida pelo helper. A conta não executa
cascade CSS/providers nem comprova todos os estados, foco, disabled/loading ou
conformidade da interface. Nessa busca dirigida sobraram dois riscos (literais e
valores equivalentes), sem achado comprovado ou impedimento de cálculo.

## Reprodução

```bash
python3 -m unittest discover -s tests -q
python3 /caminho/skill-creator/scripts/quick_validate.py skills/prismo
python3 skills/prismo/scripts/audit.py /projeto
python3 skills/prismo/scripts/audit.py /projeto --config /tmp/audit-evidence.json
node tests/storybook/catalog.test.mjs
PRISMO_JSDOM_PATH=/ambiente/node_modules/jsdom node tests/storybook/render.test.mjs
PRISMO_STORYBOOK_TEST_PACKAGE=/ambiente/package.json node tests/storybook/adapters.test.mjs
PRISMO_DOCUMENT_TEST_PACKAGE=/ambiente/package.json node tests/document/render.test.mjs
```

Testes opcionais Node usaram as dependências já disponíveis em site-easyprocess e
prismo-poc, em leitura. Não houve instalação, build ou escrita no consumidor.

## Limitações e pendências

A validação DTCG mantém o subconjunto de tokens.py e interrompe no primeiro erro;
formatos não suportados não são silenciosamente aprovados. O contraste inicial
aceita apenas cores sRGB opacas resolvidas com trecho/uso declarado. A presença de
texto numa linha não comprova sua interpretação, aplicabilidade ou ausência de
exceções. Transparência, imagens, overlays e fundos dinâmicos exigem outra evidência.

Regex/busca literal não analisa AST, bindings gerados, cascade, Semantics ou árvore
renderizada; pode gerar falsos positivos e omitir problemas. Não demonstra que todo
valor literal seja desnecessário nem que estado/variante esteja ausente. O agente
precisa conferir contratos e contexto para confirmar ou descartar riscos.

Não foram executados browser, leitor de tela, teclado/foco/zoom ou uma auditoria
WCAG completa no POC. Os testes de DOM dos templates são regressões, não teste de
acessibilidade do Button real. Roteiros em audit-scenarios.md ainda são avaliação
manual pendente; não entram na contagem de testes aprovados. Nenhum resultado aqui
concede conformidade WCAG completa ou aprova correções.
