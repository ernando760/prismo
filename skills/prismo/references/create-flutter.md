# create — Flutter

Carregue após aprovação da proposta Flutter. Siga organização de widgets, estado,
exports, theming e testes do pacote. Reutilize widgets acessíveis e bindings Dart
existentes (tema/ThemeExtension/classes geradas) com fonte DTCG identificada;
não reinterprete JSON a cada build nem duplique constantes. Não introduza state
management, Material/Cupertino ou gerador de tokens como decisão implícita.

## Implementação e catálogo

Implemente propriedades/callbacks, estados e composição no padrão local, com
contratos claros de null/disabled. Preserve TextScaler, direção de leitura,
constraints e foco aplicáveis. Semantics adicional deve complementar o widget
nativo, evitando labels duplicados ou exclusão acidental de informações.

Crie use-cases Widgetbook que importem o widget real, com os estados e combinações
pertinentes, temas aprovados, conteúdo longo e text scaling conforme escopo.
Reutilize registro manual ou anotações/generator **já usados** e confirme a API da
versão instalada. Não edite arquivos gerados manualmente; execute somente a geração
necessária se esse fluxo já existir e o diff estiver no escopo aprovado. Knobs são
exploração visual, não prova de comportamento.

Sem Widgetbook, use `paths.documentation.widgetbook` como raiz proposta para a
aplicação solicitada; preserve uma instalação existente e esclareça divergências
antes de alterar o registro. Apresente a configuração/dependências mínimas e obtenha aprovação
antes de instalar/configurar. Não crie automaticamente outro app, scaffolding de
monorepo ou pipeline build_runner. Não reutilize o template HTML de fundações
como se fosse catálogo Flutter. Casos do catálogo não substituem widget tests.

## Verificações e documentação

Implemente widget tests para conteúdo, callbacks/transições, foco/teclado e estados
pertinentes. Use Semantics e, quando aplicável, Accessibility Guideline API para
labels, contraste e tamanho de alvos. Ative Semantics no teste e libere o handle.
Use diretrizes da plataforma alvo, sem declarar equivalência automática com todos
os critérios WCAG. Exercite text scaling e restrições/RTL relevantes; evite
comparações de pixels frágeis como único teste de interação.

Execute `flutter analyze`, testes do pacote e geração/build do catálogo segundo
os comandos já existentes. Não execute comandos mutantes de setup para tornar os
testes possíveis sem aprovação. Registre bloqueios de SDK, dependências ou device;
não conte código compilável presumido ou teste não executado como aprovado.
Leitores de tela (TalkBack/VoiceOver), layout real e desempenho exigem verificação
no device/simulador quando relevantes e não são provados por Semantics unitário.

Documente propriedades/defaults/callbacks, composição, exemplos, estados/temas,
labels e foco, tokens/bindings, limitações e plataformas efetivamente verificadas.
Reutilize a documentação existente; não instale Docusaurus para esta entrega.

Fontes: [Widgetbook use-cases](https://docs.widgetbook.io/~1416/guides/use-cases),
[Flutter accessibility testing](https://docs.flutter.dev/ui/accessibility/accessibility-testing).
