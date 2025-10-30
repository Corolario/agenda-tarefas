# Agenda de Tarefas

Aplicação web de gerenciamento de tarefas desenvolvida com Flask.

## Funcionalidades

- Sistema de autenticação de usuários (registro e login)
- Adicionar, editar e deletar tarefas
- Cada usuário visualiza apenas suas próprias tarefas
- Interface responsiva e intuitiva
- Armazenamento em banco de dados SQLite

## Tecnologias Utilizadas

- **Flask** - Framework web Python
- **Flask-SQLAlchemy** - ORM para banco de dados
- **Flask-Login** - Gerenciamento de sessões de usuário
- **SQLite** - Banco de dados
- **Jinja2** - Templates HTML
- **Werkzeug** - Segurança (hash de senhas)

## Estrutura do Projeto

```
agenda/
├── flask_app/
│   ├── app.py              # Arquivo principal com rotas
│   ├── models.py           # Modelos do banco de dados
│   ├── init_db.py          # Script de inicialização do BD
│   └── templates/          # Templates HTML
│       ├── base.html
│       ├── login.html
│       ├── registro.html
│       ├── index.html
│       └── editar.html
├── requirements.txt        # Dependências Python
└── README.md
```

## Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
python flask_app/app.py
```

A aplicação estará disponível em: `http://localhost:5000`

## Uso

1. **Registro**: Acesse `/registro` para criar uma conta
2. **Login**: Faça login com suas credenciais
3. **Gerenciar Tarefas**:
   - Adicione novas tarefas com data e descrição
   - Edite tarefas existentes
   - Delete tarefas concluídas

## Segurança

- Senhas são armazenadas com hash seguro (Werkzeug)
- Cada usuário só pode acessar suas próprias tarefas
- Rotas protegidas com `@login_required`
- Validação de propriedade antes de editar/deletar

## Licença

Projeto de estudo/uso pessoal.
