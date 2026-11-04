# Cenários de diálogo de init

Avaliação manual do agente, separada dos testes determinísticos. Executar com
`$prismo init` em um projeto de teste ou em modo somente leitura. Não contar estes
cenários como testes automatizados. Não autorizar escrita em projetos reais para
avaliar um diálogo; usar uma cópia temporária quando necessário.

| Cenário | Evidência/contexto | Resultado esperado |
| --- | --- | --- |
| Projeto vazio | Sem manifestos ou decisões | Perguntar plataformas, identidade e documentação agrupadas; propor base de acessibilidade; não gravar antes de aprovação. |
| Web existente | package.json, tema CSS, src/components, .storybook | Identificar fatos com caminhos; perguntar só escopo ainda incerto; reutilizar tema e catálogo; não converter tokens legados. |
| Flutter existente | pubspec.yaml, lib/theme, Widgetbook | Reutilizar arquitetura Dart; não sugerir Storybook para Flutter; confirmar plataformas desejadas se não informadas. |
| Multiplataforma | Web e Flutter confirmados, Marketing reutiliza Web | Propor raízes distintas só quando necessárias; registrar compartilhamento; não instalar ferramentas. |
| Respostas já fornecidas | Usuário informou Web, marca pendente e documentação adiada | Não repetir perguntas; ir à proposta e aprovação. |
| Recusa ou ausência de aprovação | Proposta apresentada | Permanecer somente em leitura; não executar --apply. |
| Aprovação específica | Árvore e decisões aceitas | Criar só os caminhos apresentados; verificar saídas; informar pendências. |
| Segunda execução | Registro aprovado já existe | Ler e reutilizar decisões; relatar divergências; nenhuma reescrita automática. |
| Conflito de caminhos | Arquivo ou link no destino | Interromper escrita, preservar conteúdo e solicitar decisão sobre proposta revista. |

Os testes em `test_init.py` cobrem o preview, a materialização e a proteção dos
arquivos. Eles não comprovam que um modelo conduz corretamente a conversa.
