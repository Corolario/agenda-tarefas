# Quick Start - Deploy Rápido no VPS

## Resumo para deploy em 5 minutos

### 1. Transferir arquivos para o VPS

```bash
# Do seu computador, enviar pasta para o VPS
scp -r flask_app/ usuario@IP_DO_VPS:/home/usuario/
```

### 2. No VPS, entrar na pasta

```bash
ssh usuario@IP_DO_VPS
cd flask_app
```

### 3. Criar arquivo .env com chave secreta

```bash
# Gerar chave secreta
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Criar arquivo .env
nano .env
```

Colar no arquivo:
```env
SECRET_KEY=cole-a-chave-gerada-acima-aqui
DATABASE_URL=sqlite:///data/tarefas.db
FLASK_ENV=production
```

Salvar: `Ctrl+O`, `Enter`, `Ctrl+X`

### 4. Criar pasta de dados

```bash
mkdir -p data
```

### 5. Rodar com Docker

```bash
docker-compose up -d
```

### 6. Acessar

Abra no navegador: `http://IP_DO_SEU_VPS:5000`

**Pronto!**

- Cadastre um usuário na primeira vez
- Faça login
- Comece a usar!

---

## Comandos úteis

```bash
# Ver logs
docker-compose logs -f

# Parar
docker-compose stop

# Reiniciar
docker-compose restart

# Parar e remover tudo
docker-compose down
```

---

## Liberar porta 5000 no firewall (se necessário)

```bash
sudo ufw allow 5000/tcp
```

---

## Primeiro acesso

1. Acesse `http://IP_DO_VPS:5000`
2. Clique em "Cadastre-se"
3. Crie seu usuário
4. Faça login
5. Adicione suas tarefas!
