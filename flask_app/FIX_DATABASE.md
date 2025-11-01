# 🔧 Correção do Erro de Cadastro no Docker

## Problema Identificado

O banco de dados não estava sendo inicializado quando a aplicação rodava com Gunicorn no Docker, causando o erro **Internal Server Error** ao tentar cadastrar usuários.

## Solução Aplicada

Modificado o [Dockerfile](Dockerfile) para executar `init_db.py` antes de iniciar o Gunicorn.

---

## ⚙️ Como Aplicar a Correção no seu VPS

### 1. Transferir os arquivos atualizados

Copie os arquivos modificados para o VPS:
- `Dockerfile` (atualizado)
- `init_db.py` (atualizado)

### 2. Parar e remover containers antigos

```bash
cd /caminho/para/flask_app
docker-compose down
```

### 3. Rebuild da imagem

```bash
docker-compose build --no-cache
```

### 4. Iniciar novamente

```bash
docker-compose up -d
```

### 5. Verificar logs

```bash
docker-compose logs -f
```

Você deve ver a mensagem:
```
✓ Banco de dados inicializado com sucesso!
✓ Arquivo: sqlite:///data/tarefas.db
```

### 6. Testar

Acesse `http://seu-vps-ip:5000/registro` e tente cadastrar um usuário.

---

## 🔍 Verificar se funcionou

```bash
# Ver logs em tempo real
docker-compose logs -f web

# Verificar se o banco foi criado
ls -lh data/
# Deve aparecer: tarefas.db
```

---

## 🆘 Se ainda não funcionar

### Opção A: Criar banco manualmente

```bash
# Entrar no container
docker-compose exec web /bin/bash

# Dentro do container
python init_db.py
exit

# Reiniciar
docker-compose restart
```

### Opção B: Limpar tudo e recomeçar

```bash
# ATENÇÃO: Isso apaga todos os dados!
docker-compose down -v
rm -rf data/
mkdir -p data
chmod 755 data
docker-compose build --no-cache
docker-compose up -d
```

---

## ✅ Mudanças Feitas

### Arquivo: `Dockerfile`
- Adicionado script de inicialização que roda `init_db.py` antes do Gunicorn
- Garante que o banco de dados seja criado automaticamente

### Arquivo: `init_db.py`
- Adicionado tratamento de erros
- Não falha se o banco já existir
- Mensagens mais claras

---

## 📝 Próximos Passos

Após aplicar a correção, você pode:

1. ✅ Cadastrar usuários
2. ✅ Fazer login
3. ✅ Criar tarefas

Se tiver algum problema, verifique os logs com:
```bash
docker-compose logs -f
```
