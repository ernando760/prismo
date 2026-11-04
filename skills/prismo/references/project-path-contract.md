# Contrato de caminhos dos projetos

O registro `decisions.json` existente continua sendo a fonte de configuração; o caminho é escolhido no init e informado por `--decisions` nas operações. Na ausência de indicação permanece `design-system/decisions.json`. Não há busca automática de registros alternativos.

`foundations` mantém seu checklist `foundations-plan.json` no mesmo diretório do
registro escolhido e usa a fonte única de tokens registrada. O checklist não
substitui `decisions.json`; não exige novos campos em `decisions.paths`.

O formato `prismo_version: 1` continua válido. A extensão opcional `decisions.paths` acrescenta `packages` e `documentation` sem alterar os campos legados. Todos os caminhos locais são relativos à raiz do projeto, inclusive quando ela é o próprio pacote; `.` representa essa raiz para pacotes ou aplicações de documentação existentes. Exemplos:

```json
{"decisions": {"paths": {"decisions": "acme-ds/decisions.json", "tokens": "acme-ds/tokens.json", "components": {}, "packages": {"web": ["packages/acme-ds-web"], "flutter": ["packages/acme-ds-flutter"]}, "documentation": {"docusaurus": "docs/docusaurus", "storybook": "docs/storybook", "widgetbook": "docs/widgetbook"}}}}
```

`packages` lista raízes por plataforma; múltiplos candidatos exigem seleção explícita. `documentation` registra raízes de aplicações, não implica instalação. `components` mantém seu significado legado de raízes novas, não substitui o manifesto do pacote. Tokens são uma única fonte compartilhada registrada em `tokens`, ou fontes explícitas passadas às operações que as aceitam. O contrato não movimenta nem cria pacotes, manifestos ou aplicações de documentação. Caminhos externos não são suportados; repositórios separados usam suas próprias raízes e dependências declaradas pelos respectivos projetos.

Para uma ferramenta solicitada, o caminho registrado é a raiz da aplicação, não
necessariamente sua pasta de conteúdo ou configuração. Argumentos explícitos dos
helpers prevalecem na inspeção; divergências entre caminhos registrados e recursos
existentes exigem investigação e decisão, sem migração automática. Uma instalação
nova deve usar o caminho registrado ou apresentar alteração do registro junto à
proposta para aprovação. Sem registro, prefira instalações existentes; `docs/` é
apenas sugestão para um projeto novo. Nenhum caminho registrado prova instalação.
