# Gerenciamento de Usuários

## Criando Novos Usuários

Por segurança, o registro público de usuários foi desabilitado. Para criar novos usuários, use o script `create_user.py`:

```bash
python create_user.py
```

O script irá solicitar:
- Nome de usuário
- Senha (mínimo 6 caracteres)
- Confirmação de senha

## Exemplo de Uso

```bash
$ python create_user.py

=== Criar Novo Usuário ===

Nome de usuário: joao
Senha (mínimo 6 caracteres):
Confirme a senha:

✅ Usuário 'joao' criado com sucesso!
```

## Listando Usuários Existentes

Para ver os usuários cadastrados, você pode usar o Python:

```bash
python -c "from app import app, db; from models import User; \
with app.app_context(): \
    users = User.query.all(); \
    print('Usuários cadastrados:'); \
    [print(f'  - {u.username}') for u in users]"
```

## Deletando Usuários

Para remover um usuário:

```bash
python -c "from app import app, db; from models import User; \
username = input('Usuário a deletar: '); \
with app.app_context(): \
    user = User.query.filter_by(username=username).first(); \
    db.session.delete(user) if user else print('Usuário não encontrado'); \
    db.session.commit() if user else None; \
    print(f'Usuário {username} deletado') if user else None"
```
