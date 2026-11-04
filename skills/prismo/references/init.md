# init — inicialização guiada

## 1. Investigar antes de perguntar

Leia as instruções locais e o contexto já fornecido. Liste arquivos primeiro
(`rg --files` ou equivalente), excluindo dependências, builds e a própria skill.
Leia apenas os manifestos e trechos pertinentes: tecnologias e workspaces,
temas/tokens, componentes representativos, documentação e configurações de
catálogos. Não leia segredos, lockfiles inteiros ou o repositório todo.

Procure um registro anterior de decisões nos caminhos documentados pelo projeto;
na ausência de indicação, verifique `design-system/decisions.json`. Se existir,
reutilize decisões, confira divergências com o código e relate o estado. Não
recrie a estrutura nem reescreva esse registro automaticamente. Se outro caminho
for escolhido, comunique-o na entrega para que as demais operações o encontrem.

Diferencie fatos (com caminhos de evidência), decisões do usuário e hipóteses.
Uma dependência Flutter/Web prova tecnologia existente, não intenção de abranger
novas plataformas. Registre tokens e componentes existentes para reutilização;
não converta nem migre seu formato nesta operação.

## 2. Resolver somente lacunas essenciais

Leia [standards.md](standards.md) para aplicar as decisões técnicas compartilhadas.
Agrupe perguntas objetivas por assunto, apenas quando o projeto ou a conversa não
trouxerem respostas. Não repita respostas já dadas:

- Escopo: quais plataformas incluir agora (Web, Flutter, Marketing)? Em monorepos,
  quais aplicações/pacotes pertencem ao escopo?
- Identidade: fonte da identidade existente (marca, temas, fontes, cores)? Se não
  houver, aceitar registrar identidade pendente, sem inventar paleta ou tipografia.
- Acessibilidade: usar a base definida nos padrões; perguntar apenas por requisitos
  adicionais ou conflitos evidenciados. Uma exigência menor não permite declarar
  conformidade com a base. Nunca prometer conformidade só pela inicialização.
- Documentação: reutilizar ferramentas detectadas; confirmar adoção ou adiamento
  das ferramentas pertinentes às plataformas. Registrar alternativas existentes.

Não trate silêncio como resposta. Plataformas e locais de escrita precisam estar
resolvidos antes de executar. Identidade pendente e ferramentas adiadas são
respostas válidas. Continue a investigação independente enquanto aguarda respostas.

## 3. Apresentar proposta e aguardar aprovação

Antes de gravar qualquer arquivo no consumidor, apresente fatos e evidências,
decisões resolvidas, pendências, árvore exata de arquivos/diretórios a criar e
recursos existentes que serão reutilizados. Use caminhos relativos ao projeto.
Indique que não haverá instalação de dependências, componentes ou fundações.
Solicite aprovação dessa proposta concreta; um pedido genérico de `init` não é
aprovação da estrutura ainda desconhecida. Se a proposta mudar, solicite nova aprovação.

Prefira os locais existentes. Sem convenções, sugira `design-system/decisions.json`
e `design-system/tokens.json`. O arquivo de tokens será apenas `{}`, um contêiner
DTCG vazio, sem valores fictícios. Se já houver tokens, aponte para eles como
recurso reutilizado, mesmo se ainda não forem DTCG; registre a migração como
pendência. Nunca rotule tokens legados como DTCG validados.

Para componentes novos, registre as raízes necessárias por plataforma, sem criar
pastas vazias. Crie diretórios apenas quando houver arquivos aprovados. Reutilize
a organização existente e registre o mapeamento conceitual Atomic Design.
Para projetos novos, sugira `docs/docusaurus`, `docs/storybook` e `docs/widgetbook`
apenas para ferramentas escolhidas; locais existentes prevalecem. Os caminhos
são configuráveis e não implicam instalação ou criação das aplicações. Registre
`paths.packages` como listas de raízes por plataforma e `paths.documentation`
como caminhos das aplicações, somente quando conhecidos. Todos são relativos à
raiz do projeto; `.` representa um pacote ou aplicação na raiz. A seleção de nomes e caminhos
exige aprovação. Consulte o contrato em [contrato de caminhos](project-path-contract.md).
Pacotes próprios precisam de manifesto, nome, versão, entradas e exports adequados
quando forem realmente necessários, sem configurar publicação. Não mova projetos
existentes sem uma proposta separada e aprovação.

## 4. Criar somente o aprovado

Use `scripts/init.py` com Python 3.9+ (biblioteca padrão), relativo à pasta da skill.
O agente monta um plano JSON com as decisões e caminhos aprováveis. Pode guardá-lo
em diretório temporário, fora do consumidor, para o preview:

```json
{
  "name": "Nome do Design System",
  "platforms": ["web"],
  "identity": "Pendente; definir em foundations",
  "accessibility": "WCAG 2.2 AA; sem requisitos adicionais informados",
  "documentation": {"central": "adiada", "web": "Storybook existente"},
  "evidence": ["package.json: aplicação Web; src/theme: tema existente"],
  "reuse": ["src/theme — preservar; migração DTCG pendente"],
  "pending": ["Definir identidade visual"],
  "paths": {
    "decisions": "design-system/decisions.json",
    "tokens": null,
    "components": {}
  }
}
```

Para fonte existente, use `tokens: null` e `tokens_existing: "caminho/existente.json"` em paths; o registro indicará a fonte em `paths.tokens` sem sobrescrevê-la.
`tokens: null` evita criar tokens quando já existem ou quando sua criação foi
adiada. `components` mapeia plataformas para novas raízes, por exemplo
`{"web": "src/components"}`; deixe vazio quando reutilizar componentes existentes.
`reuse` registra também o mapeamento Atomic Design existente e os caminhos reais
de tokens/catálogos. `pending` distingue explicitamente o que continua indefinido.

```bash
python3 /caminho/da/skill/scripts/init.py /projeto --plan /tmp/plano.json
# Somente após aprovação explícita do preview pelo usuário:
python3 /caminho/da/skill/scripts/init.py /projeto --plan /tmp/plano.json --apply
```

O preview não escreve no projeto. O script não obtém aprovação: `--apply` é usado
pelo agente somente após a aprovação do usuário. Ele recusa arquivos existentes,
links nos caminhos de saída, sobreposição entre destinos e caminhos fora do
projeto. Em conflito, pare e proponha reutilização ou novo caminho; não use flags
de força nem apague arquivos. Alterações em arquivos existentes e instalações de
Docusaurus, Storybook ou Widgetbook exigem proposta e aprovação próprias; este
script não as realiza.

## 5. Verificar e entregar

Confira a saída executada, o registro de decisões e os caminhos criados. Registre
no relato final as verificações efetivamente feitas, recursos reutilizados,
pendências e localização do registro. O JSON gerado é a fonte das decisões para
as próximas operações. A inicialização não valida acessibilidade, valores de
tokens, componentes ou integrações. Em execução somente de leitura, reporte o
preview como planejamento, nunca como inicialização concluída.
