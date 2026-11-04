# create — componentes do Design System

Fluxo: **Investigar → Projetar → Aprovar → Implementar → Inspecionar → Validar**.
O conhecimento visual é interno ao Prismo; não exija nem invoque skills externas
como requisito de criação.

## Investigar

Leia instruções locais e `design-system/decisions.json` (ou caminho registrado).
Identifique fundações, identidade visual, decisões aprovadas, requisitos funcionais
e de acessibilidade e convenções da plataforma/framework. Investigue só o pacote
alvo: manifestos, componentes semelhantes e seus padrões de interação, exports, testes,
catálogo e binding dos tokens DTCG para CSS/tema Web ou Dart. Leia amostras, não
lockfiles/dependências inteiros. Busque nomes, anatomias e comportamentos equivalentes
antes de criar outro componente. Se já existir, proponha reutilizar ou um diff
localizado, sem reescrever a biblioteca.

Investigue a finalidade dos tokens semânticos em descrições DTCG, decisões,
documentação e usos aprovados. Rastreie aliases até os primitivos sem confundir
valor com papel: cores iguais não tornam tokens intercambiáveis. Confira os padrões
visuais e bindings por tema/estado; se nome, documentação e uso divergirem, exponha
a ambiguidade antes de escolher um significado.

Confirme Web ou Flutter e a tecnologia efetiva. Selecione a raiz do pacote, inclusive quando for a raiz do projeto;
em projeto multiplataforma não escolha uma plataforma silenciosamente. Web declarado
não prova framework instalado. Sem arquitetura ou decisões, esclareça as lacunas;
não faça init, configure ferramentas ou escolha framework como efeito colateral.

Pergunte só o que não estiver no projeto/conversa, agrupado por contrato visual,
API/comportamento e plataforma. Um componente decorativo pode não ter propriedades,
variantes ou interações; registre isso explicitamente. Não invente uma matriz de
estados ou tamanhos para todo componente. Classifique conceitualmente como atom,
molecule, organism, template ou page e justifique pelas responsabilidades; não
crie pastas Atomic Design se a biblioteca já tem outra organização.

## Projetar

Quando houver decisões visuais, leia [visual-design.md](visual-design.md) antes de
propor a aparência; não carregue essa referência para tarefas exclusivamente técnicas.
Use-a para definir anatomia, composição, hierarquia, distribuição, dimensões,
padding, gap, alinhamentos, tipografia, cores, bordas e elevação. Relacione cada
escolha aos tokens existentes e a exemplos aprovados no projeto. Defina apenas
variantes, tamanhos, estados, interações e adaptações responsivas necessários.
Registre regras para conteúdo longo, limites de largura e estabilidade entre estados.
Se houver lacunas, proponha alternativas fundamentadas e seus efeitos para aprovação;
não trate preferência arbitrária como decisão do Design System.

Identifique estados que podem coexistir pelas regras reais do componente. Para as
combinações relevantes, registre sinais em disputa, canais visuais (conteúdo,
superfície, contorno, ícone, foco etc.) e qual significado cada um deve comunicar.
Defina a prioridade visual pela função, comportamento, contexto e precedentes do
Design System; não adote ordem universal nem um componente obrigatório como modelo.
Proponha alternativas e peça aprovação se faltar convenção ou houver conflito entre
significados. Não resolva a disputa escolhendo apenas a cor mais contrastante.

## Aprovar

Apresente uma proposta curta e concreta, proporcional à mudança. Use os assuntos
abaixo sem exigir relatório extenso para um ajuste pequeno:

| Assunto | Decisão necessária |
| --- | --- |
| Finalidade/classificação | Nome, uso, nível Atomic e componentes a reutilizar |
| Anatomia | Partes, slots/conteúdo, composição e responsabilidades |
| API | Propriedades tipadas, defaults, eventos/callbacks e controle de estado |
| Aparência | Hierarquia/composição, dimensões/padding/gap/alinhamentos, tipografia, cores, bordas/elevação; variantes, tamanhos, temas e tokens/bindings por parte/estado |
| Responsividade | Distribuição, limites de conteúdo, larguras e comportamento adaptativo |
| Estados/comportamento | Estado inicial, interações, transições, foco/teclado, coexistência e prioridade visual contextual; significado e token de cada sinal |
| Acessibilidade | Semântica, nome acessível, estados anunciados e critérios aplicáveis |
| Entrega | Arquivos/diffs, stories/use-cases, casos de teste, docs e comandos |

Associe cada estado relevante a cenário visual e asserção funcional/acessível.
Cubra combinações que mudem o comportamento, evitando produto cartesiano sem uso.
Para conteúdo estático, documente verificações aplicáveis em vez de inventar ações.

Prefira tokens semânticos e bindings existentes; não copie os valores do JSON
para o componente ou para uma nova fonte. Se faltar binding, proponha a menor
adaptação compatível, com fonte DTCG identificada. Novo token exige motivo, busca
por equivalente, valor/alias DTCG, caminhos e diff separado visível na proposta.
Se o novo token exigir cálculo de escala ou valor de fundação, reutilize o gerador
determinístico existente e consulte somente a referência da fundação pertinente;
não calcule manualmente nem gere outra escala quando um alias existente bastar.
Inclua o preview calculado na proposta, sem persistir tokens antes da aprovação.
A aprovação pode abranger componente e esses diffs juntos, mas deve ser explícita;
a aprovação do componente sozinha não autoriza tokens/dependências não apresentados.
Preserve fundações, componentes e decisões anteriores.

Aguarde aprovação da proposta antes de criar/editar arquivos do consumidor. Pedido
genérico de create, plano com status ready, silêncio ou aprovação antiga de outra
operação não aprovam esta proposta. Mudança material de API, arquivos, tokens ou
catálogo exige reapresentar o ajuste. Não instale Storybook/Widgetbook se ausentes
sem mostrar configuração/dependências e obter aprovação. Planejado não é instalado.

## Implementar

Após aprovação, carregue **só** o guia da plataforma:
[Web](create-web.md) ou [Flutter](create-flutter.md). Confira APIs na documentação
oficial da versão instalada quando necessário; não presuma que snippets de outra
versão funcionam. Implemente o contrato aprovado com primitivas/bibliotecas locais,
sem fábrica universal de componentes, adapters multiplataforma ou novas dependências
sem necessidade. Não modifique as outras operações/fundações do Prismo.

Reutilize os harnesses de teste, temas, providers e navegação do catálogo. Stories e
use-cases importam o componente real, sem implementação paralela ou valores visuais
transcritos. Implemente as combinações aprovadas sem deixar ordem de estilos ou
resolução de estados substituir o contrato semântico. Testes devem verificar tokens/
bindings e sinais esperados nas combinações, além de comportamento e acessibilidade.
Um screenshot/golden não substitui teste de interação. Documente API,
exemplo de uso, anatomia, estados, temas, tokens, acessibilidade e limitações junto
à documentação já usada no projeto. Não instale Docusaurus para documentar um componente.

## Inspecionar

Após implementar, abra o componente real no Storybook ou Widgetbook com os recursos
de inspeção disponíveis no agente (browser, device/simulador, captura renderizada).
Reutilize o ambiente existente; não introduza dependências complexas só para inspecionar.
Aplique a lista de revisão de [visual-design.md](visual-design.md) às combinações
relevantes. Exercite interações e compare dimensões entre estados, principalmente
loading, foco e pressionamento. Registre cenários, temas, larguras e achados observados;
código, build e existência de stories não comprovam aparência. Confira se os sinais
renderizados comunicam os papéis aprovados, inclusive durante coexistência e
transições; contraste suficiente ou alias válido não comprova significado correto.

Se a inspeção visual não estiver disponível, não declare o componente visualmente
aprovado. Registre a limitação, o que foi possível verificar e as verificações
manuais pendentes. Não invente evidência a partir do helper ou de testes de DOM.

## Validar

Combine scripts determinísticos existentes para cálculos/contrastes (por exemplo,
`colors.py contrast`, com argumentos consultados em `--help`), testes funcionais de
interações/estados, testes automatizados de acessibilidade quando disponíveis e
inspeção visual. Calcule contraste com as cores efetivamente renderizadas; aliases,
transparência e fundos devem ser resolvidos antes do cálculo. Não duplique validadores.
Execute build/análise e checagens relevantes da plataforma. Para bibliotecas Web
distribuíveis, valide também o tarball em consumidor isolado conforme
[create-web.md](create-web.md#pacotes-distribuíveis), incluindo exports, declarações,
CSS e resoluções TypeScript aplicáveis; build do catálogo não substitui essa etapa. Teste planejado, ignorado
ou bloqueado não é aprovado; informe comando, resultado e limites da evidência
(DOM simulado versus browser, Semantics versus leitor de tela real).

Diferencie problemas comprovados (com reprodução/evidência), riscos potenciais
(hipótese e impacto) e verificações manuais pendentes (cenário e motivo).
Corrija problemas dentro do escopo aprovado e repita as verificações afetadas;
alterações de decisões estabelecidas ou expansão material exigem nova aprovação.

Confira o diff e o binding aos tokens, além de preservação das fundações e outros
componentes. Entregue arquivos, catálogo/docs, resultados e pendências. Se o projeto
mantiver registro de componentes, atualize-o no formato existente, preservando
as demais seções; não imponha outro registro ou reescreva decisions.json sem diff
apresentado. Não declare conclusão integral se catálogo ou testes exigidos faltarem.

## Helper opcional de revisão

Para conferir caminhos/tokens e cobertura declarada de estados, use
`scripts/create.py` com Python 3.9+, sem pacotes externos. Monte o plano em diretório
temporário fora do consumidor, a partir do [modelo](../assets/templates/create-plan.json).
O modelo começa incompleto; não preencha perguntas essenciais por suposição.
Anatomia/API/justificativas continuam na proposta humana; não precisam de outro schema.

```bash
python3 /caminho/da/skill/scripts/create.py /projeto --plan /tmp/component-plan.json
```

O helper não escreve, executa comandos, instala ou obtém aprovação. Exit 0:
`proposal_ready`, ainda exigindo aprovação; 2: `needs_input`; 1: erro de entrada.
Confere evidências básicas da raiz, existência/cadeias de aliases, arquivos e estados
cobertos por casos. Não valida valor DTCG completo, binding em runtime, contrato de
API ou qualidade dos testes. `checks.command` é inventário: revise contexto e execute
os comandos pelo fluxo normal após aprovação, nunca via execução cega do JSON.
Para fontes DTCG em vários arquivos, aponte o agregador existente ou investigue-os
manualmente; não gere uma cópia persistente para satisfazer o helper.

A raiz do projeto continua sendo a base dos caminhos de decisões, tokens e arquivos.
No helper use `--package-dir packages/nome` para identificar o manifesto do pacote;
se houver um único pacote registrado para a plataforma ele é selecionado, e múltiplos
candidatos exigem seleção explícita. Componentes e exports pertencem à biblioteca;
catálogos são aplicações consumidoras. Preserve nomes e caminhos existentes.
Prepare manifesto, versão e API pública quando necessários e aprovados, sem publicar.

Antes de aprovar setup de catálogo, confira `paths.documentation` para a ferramenta
solicitada e inclua caminho, manifesto, scripts, globs/registro e dependência do
pacote selecionado no diff. Um catálogo existente fora do caminho registrado exige
esclarecimento; não o mova nem crie outro por inferência. Para demonstrar consumo,
verifique nome e versão da biblioteca no manifesto, declaração de dependência no
catálogo, entradas/exports públicos, import do componente real e resolução efetiva
no ambiente da ferramenta. Use o build e testes existentes da aplicação com a
versão instalada. Em Flutter confira `pubspec.yaml`, import `package:` e barrel
público; em Web confira manifesto, exports e resolução do builder. Execute apenas
comandos aprovados e disponíveis; não conte leitura de arquivo ou import declarado
como prova de resolução. Registre bloqueios, inclusive SDK ausente. Não copie a
implementação do componente para stories ou use-cases.
