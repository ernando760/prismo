# Visual Design — decisões e inspeção de componentes

Leia ao projetar ou revisar aparência no fluxo create. Este guia contém critérios
visuais; contrato, aprovação, implementação e entrega ficam em [create.md](create.md).
Parta de componentes aprovados e fundações do consumidor. Não imponha estética,
paleta, fonte, escala, raio ou sombra novos. Para cada escolha, identifique o papel,
o precedente e o token/binding; uma lacuna vira alternativa justificada na proposta.

## Hierarquia e composição

- Determine a informação ou ação principal pela tarefa. Diferencie prioridade com
  os recursos já usados pelo sistema (posição, agrupamento, peso, tamanho ou cor);
  se vários elementos disputarem atenção, reduza a ênfase dos secundários.
- Agrupe conteúdo que é interpretado junto; separe grupos por espaço antes de
  acrescentar divisores. Compare o peso visual de ícones, texto e ações, incluindo
  estados sem ícone ou sem descrição. Não preencha espaços com decoração sem função.
- Escolha eixo, proporções e alinhamentos pela leitura e pelo componente equivalente.
  Alinhe textos por baseline quando compartilham uma linha; centralize controles
  quando essa for a relação esperada. Confira ícones assimétricos opticamente:
  caixas iguais não garantem centros visuais iguais. Não corrija com offsets mágicos
  antes de verificar caixa do asset, line-height e convenções de ícones existentes.
  Avalie a proporção da área desenhada do ícone em relação ao texto e seu peso
  visual; use tamanhos locais e não confunda tamanho do ícone com área interativa.

## Tipografia

- Escolha papéis tipográficos existentes para rótulo, valor, título e ajuda. Crie
  distinção suficiente para a tarefa sem inventar uma escala para cada componente.
  Texto secundário precisa continuar legível; não reduza contraste para ocultá-lo.
- Defina line-height pelo papel e pelo conteúdo: múltiplas linhas precisam respirar;
  rótulos de controles devem caber sem cortes. Verifique ascendentes, descendentes,
  acentos e fonte efetivamente carregada, não apenas a altura declarada.
- Use pesos disponíveis na fonte. Avalie quebra de linha e alinhamento de números,
  ícones e texto; preserve a direção de leitura e o alinhamento adotado no sistema.
  Truncamento exige motivo e acesso ao conteúdo completo; não o use para esconder
  um problema de composição. Teste ampliação de texto sem sobreposição.

## Espaçamento e dimensões

- Selecione padding e gap na escala existente pela densidade e parentesco do conteúdo.
  A distância dentro de um grupo deve comunicar relação mais próxima que a distância
  entre grupos. Compare com componentes vizinhos, evitando uma escala local isolada.
- Derive altura do conteúdo, line-height, padding e bordas; prefira altura mínima
  quando texto pode crescer. Largura fixa só quando o uso a exige. Verifique se o
  espaço para ícones e indicadores preserva área útil e alinhamento do texto.
- Compare variantes lado a lado. Reserve espaço de loading/indicadores quando a
  troca causaria salto; mantenha métricas de borda entre estados e desenhe foco sem
  alterar o fluxo. Não fixe dimensões que causem clipping só para evitar movimento.

## Cores, bordas e elevação

- Mapeie superfície, conteúdo, ação, seleção, erro e foco a tokens semânticos e aos
  bindings de cada tema. Escolha pares de primeiro plano/fundo, não cores isoladas.
  Confira o significado dos papéis no contrato de create; não substitua um token
  por outro só porque têm o mesmo valor. Não derive o tema escuro por inversão nem
  use cor como único sinal de estado.
- Verifique contraste do par efetivo em cada estado aplicável com o script existente,
  considerando transparência e fundos. Identifique o critério pelo uso (texto,
  texto grande, controle/indicador); um resultado para texto não valida todo o componente.
- Use contorno para delimitar ou comunicar estado e elevação para relações de camada,
  conforme precedentes locais. Não acumule sombra e borda sem função. Escolha raios
  pela família e tamanho do componente; confira encaixe de superfícies aninhadas.
  No tema escuro, verifique separação de camadas sem depender só da sombra.

## Interações e acessibilidade

- Compare default com hover, focus, error, disabled, pressed e loading quando
  aplicáveis. Defina o sinal visual de cada estado conforme os padrões locais;
  nome de token diferente não comprova diferença perceptível. Confira combinações como error com focus quando relevantes
  e e a distribuição de sinais conforme o contrato aprovado; confira se
  a composição preserva os significados necessários e os requisitos de acessibilidade,
  sem aplicar uma precedência fixa entre estados.
  Hover não pode ser a única forma de descobrir uma ação. Preserve rótulo/nome
  acessível em loading.
- Mantenha foco visível, não recortado e reconhecível sobre fundos adjacentes.
  Área interativa e separação entre alvos devem seguir os requisitos da plataforma;
  o ícone visível pode ser menor que seu alvo. Confira teclado e toque, não só mouse.
- Transições devem explicar a mudança sem atrasar a ação. Use duração/easing locais
  e evite animar dimensões quando isso deslocar conteúdo sem propósito. Respeite
  movimento reduzido removendo ou simplificando movimento não essencial, mantendo
  feedback perceptível. Estados acessíveis devem acompanhar o estado visual real.

## Responsividade

- Defina limites a partir do conteúdo e dos padrões locais: quando quebrar linha,
  empilhar ações ou redistribuir slots. Preserve ordem de leitura, prioridade e alvos.
  Não reduza fonte ou área de toque apenas para caber numa largura estreita.
- Teste largura mínima suportada, intermediária e ampla, além de texto longo,
  localização, ampliação de texto e RTL quando pertinentes. Decida explicitamente
  entre quebra, expansão, rolagem ou truncamento; não dependa de overflow acidental.

## Revisão do renderizado

Compare o componente real com a proposta e os equivalentes aprovados. Selecione
casos que exercitem diferenças reais, sem produto cartesiano de todas as opções:

- Alinhamento horizontal, vertical, baseline e óptico; distribuição de texto, ícones
  e indicadores; legibilidade, hierarquia, padding e gaps internos/externos.
- Dimensões entre variantes/tamanhos e de default para hover, focus, error, pressed,
  disabled e loading aplicáveis. Observe deslocamentos inesperados, quebra de texto,
  cortes e mudanças de largura/altura, inclusive durante a transição.
- Conteúdo curto, longo e opcional nas larguras relevantes; texto ampliado e
  comportamento responsivo. Verifique também o componente junto a seus vizinhos.
- Temas claro e escuro quando suportados; contraste, separação de superfícies,
  foco e feedback dos estados isolados e coexistentes. Compare o significado de
  cada sinal com o contrato e os precedentes locais, não apenas suas cores.
  Tema ausente não deve ser inventado na inspeção.
- Transições em uso real e com movimento reduzido; consistência entre aparência,
  interação e estado acessível. Uma captura estática não comprova movimento ou teclado.

Registre o cenário observado e a evidência. Sem renderização inspecionada, mantenha
aprovação visual pendente, mesmo que testes, contrastes e build passem. Medidas e
scanners comprovam aspectos específicos; julgamento de hierarquia e equilíbrio
exige inspeção. Riscos e verificações pendentes não são defeitos comprovados.
