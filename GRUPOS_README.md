# Sistema de Grupos de Tarefas

Este documento descreve as novas funcionalidades de grupos de tarefas implementadas no sistema.

## Visão Geral

O sistema agora suporta:

- **Usuários Administradores**: Podem criar grupos de tarefas e usuários comuns
- **Grupos de Tarefas**: Conjuntos de usuários que compartilham tarefas
- **Permissões Granulares**: Controle sobre quem pode ver e editar tarefas

## Tipos de Usuários

### Usuário Administrador
- Cria grupos de tarefas
- Cria usuários comuns via interface web
- Gerencia membros dos grupos
- Pode editar/deletar tarefas de qualquer usuário de seus grupos
- Criado apenas via script `create_user.py`

### Usuário Comum
- Pertence a um ou mais grupos de tarefas
- Vê todas as tarefas dos grupos que pertence
- Pode editar/deletar apenas suas próprias tarefas
- Criado por administradores via interface web

## Funcionalidades

### 1. Criação de Usuários

#### Criar Administrador (via script)
```bash
python create_user.py
# Responda as perguntas:
# - Nome de usuário: admin
# - Senha: ******
# - Confirmar senha: ******
# - É administrador? s
```

#### Criar Usuário Comum (via web)
1. Login como administrador
2. Acesse "Administração" no header
3. Clique em "+ Novo Usuário"
4. Preencha username e senha
5. Clique em "Criar Usuário"

### 2. Gerenciamento de Grupos

#### Criar Grupo
1. Login como administrador
2. Acesse "Administração" → "Gerenciar Grupos de Tarefas"
3. Clique em "+ Novo Grupo"
4. Preencha nome e descrição (opcional)
5. Clique em "Criar Grupo"

#### Adicionar Membros ao Grupo
1. Na lista de grupos, clique em "Gerenciar Membros"
2. Selecione um usuário no dropdown
3. Clique em "Adicionar"

#### Remover Membro do Grupo
1. Na página de membros do grupo
2. Clique em "Remover" ao lado do usuário desejado

### 3. Gerenciamento de Tarefas

#### Criar Tarefa
1. Na página principal, clique em "+ Nova Tarefa"
2. Selecione o grupo de tarefas
3. Escolha a data
4. Digite a descrição
5. Clique em "Adicionar Tarefa"

#### Visualizar Tarefas
- Todos os usuários veem as tarefas de todos os membros do grupo
- A coluna "Criado por" mostra quem criou cada tarefa
- Suas tarefas aparecem com "Você" na coluna

#### Editar Tarefa
- **Usuário Comum**: Só pode editar suas próprias tarefas
- **Administrador**: Pode editar qualquer tarefa de seus grupos

#### Deletar Tarefa
- **Usuário Comum**: Só pode deletar suas próprias tarefas
- **Administrador**: Pode deletar qualquer tarefa de seus grupos

## Inicialização do Sistema

Na primeira execução, a aplicação criará automaticamente o banco de dados com todas as tabelas necessárias:

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar aplicação (cria o banco automaticamente)
python app.py

# Em outro terminal, criar o primeiro usuário administrador
python create_user.py
```

## Estrutura do Banco de Dados

### Tabela `users`
- `id`: Identificador único
- `username`: Nome de usuário
- `password_hash`: Hash da senha
- `is_admin`: Se é administrador (true/false)
- `created_at`: Data de criação

### Tabela `task_groups`
- `id`: Identificador único
- `name`: Nome do grupo
- `description`: Descrição (opcional)
- `admin_id`: ID do administrador responsável
- `created_at`: Data de criação

### Tabela `user_taskgroup`
- `user_id`: ID do usuário
- `taskgroup_id`: ID do grupo
- Relacionamento many-to-many entre usuários e grupos

### Tabela `tarefas`
- `id`: Identificador único
- `data`: Data da tarefa
- `descricao`: Descrição da tarefa
- `user_id`: ID do usuário que criou
- `task_group_id`: ID do grupo (obrigatório)
- `created_at`: Data de criação

## Fluxo de Trabalho Típico

1. **Administrador cria o ambiente**:
   - Criar usuário administrador via script
   - Login no sistema
   - Criar grupo de tarefas (ex: "Equipe de Desenvolvimento")
   - Criar usuários comuns
   - Adicionar usuários ao grupo

2. **Usuários comuns trabalham**:
   - Login no sistema
   - Ver todas as tarefas do grupo
   - Criar suas próprias tarefas
   - Editar/deletar apenas suas tarefas
   - Acompanhar tarefas dos colegas

3. **Administrador supervisiona**:
   - Ver todas as tarefas
   - Editar/deletar tarefas de qualquer usuário
   - Gerenciar membros dos grupos
   - Criar novos grupos conforme necessário

## Interface de Administração

Acessível apenas para administradores:

- **Dashboard**: Visão geral de grupos e usuários
- **Grupos de Tarefas**: Lista, cria, edita e deleta grupos
- **Membros do Grupo**: Adiciona e remove usuários dos grupos
- **Criar Usuário**: Cria novos usuários comuns

## Segurança

- Senhas são armazenadas com hash usando Werkzeug
- Verificação de permissões em todas as rotas
- Admin só pode gerenciar seus próprios grupos
- Usuários comuns não têm acesso à área administrativa
- Validação de pertencimento ao grupo antes de operações

## Solução de Problemas

### "Você não pertence a nenhum grupo de tarefas"
- Entre em contato com um administrador
- Se você é admin, crie um grupo e adicione-se como membro

### "Você não tem permissão para editar esta tarefa"
- Usuários comuns só podem editar suas próprias tarefas
- Verifique se a tarefa foi criada por você

### Não consigo acessar a área de administração
- Apenas usuários criados como administradores têm acesso
- Use o script `create_user.py` para criar administradores

## Comandos Úteis

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar aplicação (cria banco automaticamente na primeira execução)
python app.py

# Criar usuário administrador
python create_user.py
```

## Arquitetura

### Modelos
- `User`: Usuários do sistema
- `TaskGroup`: Grupos de tarefas
- `Tarefa`: Tarefas individuais
- `user_taskgroup`: Tabela associativa

### Rotas Principais
- `/`: Lista de tarefas
- `/admin`: Dashboard de administração
- `/admin/groups`: Gerenciar grupos
- `/admin/users/create`: Criar usuários

### Templates
- `index.html`: Lista de tarefas
- `admin/dashboard.html`: Painel admin
- `admin/groups.html`: Lista de grupos
- `admin/group_members.html`: Gerenciar membros
- `admin/create_user.html`: Criar usuário
- `admin/create_group.html`: Criar grupo
