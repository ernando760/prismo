# audit — qualidade e consistência, somente leitura

Consulte [naming.md](naming.md) quando houver convenção de tokens a registrar ou aplicar; preserve decisões e nomes existentes.

## Investigar com escopo

Leia instruções locais e decisões aprovadas, normalmente
`design-system/decisions.json`. Identifique plataformas/pacotes, fontes DTCG e
agregação/temas, fundações, bindings, componentes e seus testes, documentação
canônica e Storybook/Widgetbook. Use busca e amostras relevantes, não carregue todas
as operações. Só consulte referência de outra operação se houver dúvida específica
sobre um formato/contrato. Sem escopo, faça uma auditoria inicial curta e declare
o que cobriu. Pergunte só lacunas que impeçam avaliar um uso real.

Auditar não corrige, instala, regenera, atualiza snapshots, edita decisões, escreve
relatórios no consumidor ou publica nada. Não execute scripts de package.json,
configuração JS, testes/builds com efeitos desconhecidos ou flags fix/update.
Se uma verificação exigir execução que escreve, use ambiente isolado e entradas
copiadas com escopo mínimo, saídas/caches fora do consumidor; caso contrário,
registre como pendente. Não considere teste existente no repositório como teste
executado nesta auditoria. Não peça aprovação para leitura já autorizada.

## Evidências e verificações

| Área | Como verificar sem inferir defeitos |
| --- | --- |
| Tokens | Reutilizar `scripts/tokens.py`/validadores: tipos efetivos, aliases/campos compostos, alvos, ciclos, colisões e duplicação de chaves/caminhos. Valores equivalentes são candidatos, não consolidação obrigatória. Temas com caminhos alternativos são contextos separados |
| Fundações | Confrontar escalas, papéis, unidades e projeções Web/Flutter com decisões aprovadas e documentação. Conferir exceções e passos personalizados antes de alegar deriva; não regenerar escalas ou paletas durante audit |
| Componentes | Rastrear token → binding/tema → propriedade/estado. Procurar literais em estilos Web e Dart e conferir finalidade: zero, hairline, full, assets, layout e fallbacks podem ser intencionais. Ausência de string não comprova ausência de uso |
| Consistência | Comparar anatomia, API/defaults, variantes/tamanhos/estados e comportamento nas fontes reais, docs e catálogo, respeitando geração/parametrização. Um contrato deve vir de decisões/API/uso aprovado, não de uma matriz universal inventada |
| Acessibilidade | Verificar semântica, nome, foco/teclado, estados anunciados, erros/loading/disabled aplicáveis e responsabilidades do consumidor. Inspeção estática gera riscos; confirmação pode exigir runtime, Semantics/DOM e teste manual |
| Contraste | Identificar par primeiro plano/fundo adjacente, tema, estado e uso real; calcular por `colors.contrast`/`evaluate`. Não cruzar todas as paletas nem assumir pares por nome de token |

Para WCAG 2.2 AA, 1.4.3 usa 4.5:1 em texto normal e 3:1 em texto grande; confirme
tamanho/peso antes de classificar como grande. 1.4.11 exige 3:1 para informação
visual necessária em controles/estados/gráficos contra cores adjacentes aplicáveis.
Não trate todo contorno decorativo como requisito nem compare hover/default como
se fossem cores adjacentes. Confira exceções (por exemplo, controles inativos),
transparência, fundos/gradientes, overlays e contextos reais. A decisão AA usa a
razão sem arredondamento. Cálculo numérico de um par declarado é comprovável;
a aplicação/violação no componente exige confirmar esse contexto.

Fontes oficiais: [1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
e [1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).
Uma checagem automatizada não comprova conformidade WCAG completa.

## Helper opcional determinístico

```bash
python3 /skill/scripts/audit.py /projeto
python3 /skill/scripts/audit.py /projeto --config /tmp/audit-evidence.json --scope src --scope docs
# Excluir artefatos locais ou módulos de apresentação copiados pelo projeto:
python3 /skill/scripts/audit.py /projeto --scope src --exclude src/prismo --exclude src/generated.css
# Fontes divididas, mesmo contexto de resolução:
python3 /skill/scripts/audit.py /projeto --source ds/base.json --source ds/semantic.json
```

Python 3.9+, biblioteca padrão; saída JSON somente stdout. O helper desativa escrita
de bytecode e não executa comandos/configurações do consumidor. Reutiliza os
validadores de tokens e cálculos de Colors, sem alterar outras operações.
Sem `--source`, consulta `paths.tokens`; `--decisions` admite registro customizado.
`--scope` limita busca de evidências textuais, não as fontes explicitamente indicadas.
`--exclude` é repetível: caminho literal de arquivo ou diretório relativo à raiz do
projeto, mesmo com `--scope` em subdiretório; exclui também descendentes. Não aceita
glob, caminho absoluto, `..` ou symlink; pode nomear destino ainda inexistente.
As exclusões não impedem ler decisões nem validar fontes DTCG declaradas, inclusive
por `--source`. Evidências excluídas ficam não verificadas/manuais, nunca aprovadas.

A busca poda dependências/builds existentes e diretórios `storybook-static`,
`.cache`, `.turbo`, `.nuxt`, `.output`, `.svelte-kit`, `.vercel`, `.angular` e
`.pytest_cache`, inclusive aninhados ou selecionados em `--scope`; ignora sufixos
`.min.js`, `.min.css`, `.g.dart`, `.freezed.dart`. Esses filtros atuam antes do limite
de arquivos. Não ignora todo CSS nem diretórios genéricos de fontes: bindings de
tokens e implementações podem ser relevantes. Para saídas com nomes próprios e
cópias de renderers do Prismo, investigue os caminhos e use `--exclude` explícito.
Não detecta automaticamente todo arquivo gerado nem interpreta `.gitignore`.
`coverage` informa escopos, exclusões, diretórios/sufixos ignorados e truncamento;
`skipped` conta entradas/subárvores descartadas, sem percorrer seus descendentes.

O [modelo opcional](../assets/templates/audit-evidence.json) contém três campos:

- `contrast_pairs`: cada par tem `foreground`, `background` (caminhos DTCG),
  `usage` (`normal_text`, `large_text`, `non_text`) e `evidence` com `file`, `line`
  (base 1) e `text` encontrado nessa linha. Monte a partir de usos investigados,
  preservando contexto/tema na explicação. O helper confere a presença do trecho,
  não interpreta se ele realmente demonstra o relacionamento declarado.
- `bindings`: mapa de token → nomes de código conhecidos. Se um binding observado
  apontar para token não encontrado nas fontes fornecidas, sinaliza risco a conferir.
- `components`: itens com `name`, `implementation`, `documentation`, `catalog`
  (caminhos relativos ou null) e `expectations`. Cada expectativa tem `name` e os
  mesmos três papéis, com literais esperados ou null (não verificar esse papel).
  Use assinaturas/nomes extraídos do contrato, não regex arbitrária ou decisões novas.
  Literal ausente é risco de cobertura textual, nunca prova de estado ausente.

Config pode ficar em temporário fora do consumidor; nenhum arquivo novo nele é
necessário. Não gere evidência ou exemplos ausentes para satisfazer o helper.
Exit 0: sem achados comprovados (pode haver riscos/pendências); 2: achados
comprovados; 1: entrada/config inválida ou erro que impediu o relatório. Zero não
é aprovação do Design System. Cálculos de pares sustentados por trecho e cores
opacas resolvidas são registrados mesmo se passarem; falhas numéricas são achados
sobre o par declarado, sem declarar violação de uma interface não inspecionada.

## Classificar e relatar

Cada achado deve trazer severidade, certeza, evidência/localização, impacto e ação
recomendada. Caminho de token/arquivo é válido quando não houver linha confiável;
não invente números de linha. Use:

- **Comprovado**: observação/conta reproduzível com escopo claro, como ciclo, JSON
  inválido ou razão insuficiente no par declarado. Confirme violação em runtime
  somente com evidência apropriada.
- **Risco**: indício contextual, como literal possivelmente substituível por token,
  API/docs divergentes em busca textual ou nomes de variantes não encontrados.
- **Manual pendente**: falta evidência, formato não suportado ou execução indisponível.
  Ausência de teste/catalog/config em uma busca parcial não é defeito comprovado.

Severidade **alta**: contrato/fonte quebrada ou conta AA insuficiente em uso declarado;
**média**: possível deriva/uso/acessibilidade com impacto a confirmar; **baixa**:
consolidação potencial ou informação a localizar. Ajuste pela evidência e impacto
real, sem inventar severidade crítica ou elevar todo indício.

Resuma primeiro os achados relevantes, agrupando repetições por causa/arquivo e
prioridade. Se não houver problemas relevantes, informe resultado e limites em
poucas linhas; não liste cada token aprovado. Não converta riscos do helper em
problemas confirmados sem investigar. Valores iguais, medidas estruturais aprovadas
e referências geradas podem ser descartados como falsos positivos com justificativa.
Inclua comandos realmente executados, bloqueios e próximos passos manuais; correções
pertencem a tarefa separada, com aprovação própria.

## Cobertura inicial e limites

O helper valida o subconjunto DTCG de `tokens.py`: interrompe no primeiro erro do
conjunto e distingue formatos não suportados de falhas comprováveis. Consulte o
pipeline local para `$ref`/`$extends`, outras cores e recursos não suportados, sem
converter a fonte. Contraste inicial: sRGB opaco; transparência/composição, usos
não identificados e fontes inválidas ficam pendentes, sem aprovação fictícia.

Busca literal limitada a texto UTF-8 de até 1 MiB/arquivo, 5.000 arquivos por padrão;
ignora dependências/builds/lockfiles/symlinks, pode ter falsos positivos/negativos e
não analisa AST, cascade CSS, providers ou runtime. Detecta alguns literais Web/Dart
e img sem alt explícito; não substitui análise do agente, teste de leitor de tela,
zoom/teclado, semântica Flutter, revisão visual dos temas ou auditoria completa.
Relatório limita 100 achados e 10 registros de pares (falhas/pendências primeiro),
prioriza severidade e informa totais/omitidos/escopo. Restrinja a entrada para obter
detalhes dos pares omitidos, sem repetir checagens já conclusivas por padrão.

Com política registrada, avalie nomes separadamente do DTCG. Aliases com o mesmo alvo são candidatos para revisão de intenção, não redundâncias comprovadas.
