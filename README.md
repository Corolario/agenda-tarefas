# Gerenciador de Tarefas - Flask

Aplicação web colaborativa para gerenciamento de tarefas com sistema de grupos e autenticação.

## Funcionalidades

### Para Usuários Comuns
- Sistema de login seguro com autenticação
- Visualizar tarefas de todos os membros do grupo
- Adicionar, editar e deletar suas próprias tarefas
- Filtrar tarefas por usuário ou grupo
- Ver quem criou cada tarefa
- Interface responsiva e moderna

### Para Administradores
- Criar e gerenciar grupos de tarefas
- Criar usuários comuns via interface web
- Adicionar/remover membros dos grupos
- Editar e deletar tarefas de qualquer usuário do grupo
- Visualização em tempo real de membros e tarefas por grupo

## Diferenciais

- **Grupos de Tarefas**: Organize equipes e compartilhe tarefas
- **Permissões Granulares**: Controle sobre quem pode editar cada tarefa
- **Filtros Inteligentes**: Por usuário e por grupo
- **Interface Intuitiva**: Design limpo e fácil de usar
- **Banco de Dados SQLite**: Leve e sem necessidade de servidor externo

## Tecnologias

- **Flask** - Framework web
- **Jinja2** - Template engine
- **Flask-Login** - Autenticação
- **SQLAlchemy** - ORM para banco de dados
- **Docker** - Containerização
- **Gunicorn** - Servidor WSGI para produção

## Início Rápido

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/agenda-tarefas.git
cd agenda-tarefas

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie a aplicação (o banco é criado automaticamente)
python app.py

# 4. Em outro terminal, crie o primeiro administrador
python create_user.py
```

Acesse: http://localhost:5000

### Primeiros Passos

1. **Login** com o usuário administrador criado
2. Acesse **Administração** no header
3. **Crie um Grupo de Tarefas** (ex: "Equipe de Desenvolvimento")
4. **Adicione-se como membro** do grupo
5. Volte para a página principal e **crie sua primeira tarefa**!

Veja documentação completa em [GRUPOS_README.md](GRUPOS_README.md)

---

## Estrutura do Projeto

```
agenda-tarefas/
├── app.py                    # Aplicação principal Flask
├── models.py                 # Modelos do banco de dados (User, TaskGroup, Tarefa)
├── create_user.py            # Script para criar usuários (admin via CLI)
├── init_db.py               # Script de inicialização do banco
├── templates/                # Templates Jinja2
│   ├── base.html            # Template base
│   ├── login.html           # Página de login
│   ├── index.html           # Lista de tarefas (com filtros)
│   ├── editar.html          # Edição de tarefa
│   └── admin/               # Templates de administração
│       ├── dashboard.html   # Painel de controle
│       ├── create_group.html
│       ├── edit_group.html
│       ├── group_members.html
│       └── create_user.html
├── instance/                 # Banco de dados SQLite (criado automaticamente)
├── requirements.txt          # Dependências Python
├── Dockerfile                # Configuração Docker
├── docker-compose.yml        # Orquestração Docker
├── README.md                 # Este arquivo
└── GRUPOS_README.md          # Documentação do sistema de grupos
```

---

## Deploy no VPS com Docker Compose

### Pré-requisitos no VPS

1. **Docker** instalado
2. **Docker Compose** instalado
3. **Git** (opcional, para clonar repositório)

### Passo 1: Instalar Docker e Docker Compose (se necessário)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker (opcional, evita usar sudo)
sudo usermod -aG docker $USER
newgrp docker

# Instalar Docker Compose
sudo apt install docker-compose -y

# Verificar instalação
docker --version
docker-compose --version
```

### Passo 2: Transferir arquivos para o VPS

**Opção A: Via Git**
```bash
# No VPS
cd /home/seu-usuario
git clone https://seu-repositorio.git
cd flask_app
```

### Passo 3: Configurar variáveis de ambiente

```bash
# No VPS, dentro da pasta flask_app/
cd /home/usuario/flask_app

# Criar arquivo .env
nano .env
```

Conteúdo do arquivo `.env`:
```env
SECRET_KEY=sua-chave-secreta-muito-segura-aqui-gere-uma-aleatoria
DATABASE_URL=sqlite:///data/tarefas.db
FLASK_ENV=production

# Configurar UID/GID para evitar permissões de root no diretório data/
UID=1000
GID=1000
```

**Dica para gerar SECRET_KEY segura:**
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

**Dica para obter seu UID e GID:**
```bash
# Ver seu UID
id -u

# Ver seu GID
id -g
```

### Passo 3.1: Corrigir Permissões (SOLUÇÃO RÁPIDA)

**Se o diretório `data/` foi criado como root e o Docker está em loop de restart**, use o script de correção:

```bash
# Executar script de correção automática
./fix-permissions.sh
```

Este script irá:
- ✅ Corrigir permissões do diretório `data/` se necessário
- ✅ Criar arquivo `.env` com UID/GID corretos
- ✅ Configurar tudo automaticamente

**OU faça manualmente:**
```bash
# Corrigir permissões do diretório data/
sudo chown -R $USER:$USER data/

# Adicionar UID/GID ao .env
echo "UID=$(id -u)" >> .env
echo "GID=$(id -g)" >> .env
```

### Passo 4: Criar diretório para dados

```bash
mkdir -p data
```

### Passo 5: Build e executar com Docker Compose

```bash
# Build da imagem
docker-compose build

# Iniciar a aplicação
docker-compose up -d

# Verificar se está rodando
docker-compose ps
docker-compose logs -f
```

### Passo 6: Acessar a aplicação

A aplicação estará rodando em: `http://ip-do-seu-vps:5000`

**Exemplo:** `http://192.168.1.100:5000`

---

## Configurar Nginx como Reverse Proxy (Opcional, mas recomendado)

Para usar um domínio e HTTPS:

### Instalar Nginx

```bash
sudo apt install nginx -y
```

### Configurar site

```bash
sudo nano /etc/nginx/sites-available/tarefas
```

Conteúdo:
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Ativar site

```bash
sudo ln -s /etc/nginx/sites-available/tarefas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Configurar HTTPS com Let's Encrypt (Opcional)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Renovação automática (já configurado automaticamente)
sudo certbot renew --dry-run
```

---

## Comandos Úteis

### Gerenciar containers

```bash
# Ver logs
docker-compose logs -f

# Parar aplicação
docker-compose stop

# Iniciar aplicação
docker-compose start

# Reiniciar aplicação
docker-compose restart

# Parar e remover containers
docker-compose down

# Rebuild após alterações no código
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup do banco de dados

```bash
# Fazer backup
cp data/tarefas.db data/tarefas_backup_$(date +%Y%m%d).db

# Ou compactar
tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

### Ver logs da aplicação

```bash
docker-compose logs -f web
```

### Acessar container (debug)

```bash
docker-compose exec web /bin/bash
```

---

## Desenvolvimento Local

### Sem Docker

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python app.py
```

Acesse: http://localhost:5000

### Com Docker

```bash
docker-compose up
```

Acesse: http://localhost:5000

---

## Solução de Problemas

### Container em loop de restart (problema de permissões)

**Sintoma:** O container fica reiniciando continuamente e o diretório `data/` foi criado como root.

**Solução:**
```bash
# 1. Parar os containers
docker-compose down

# 2. Executar script de correção
./fix-permissions.sh

# 3. Rebuild e iniciar
docker-compose build
docker-compose up -d
```

**OU manualmente:**
```bash
# Parar containers
docker-compose down

# Corrigir permissões
sudo chown -R $USER:$USER data/

# Garantir que UID/GID estão no .env
echo "UID=$(id -u)" >> .env
echo "GID=$(id -g)" >> .env

# Rebuild e iniciar
docker-compose build
docker-compose up -d
```

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs

# Verificar se a porta 5000 está em uso
sudo netstat -tulpn | grep 5000

# Reiniciar do zero
docker-compose down -v
docker-compose up -d
```

### Banco de dados corrompido

```bash
# Parar aplicação
docker-compose down

# Remover banco (ATENÇÃO: perde todos os dados)
rm data/tarefas.db

# Reiniciar
docker-compose up -d
```

### Permissões no diretório data/

**O diretório `data/` é criado automaticamente com as permissões corretas do seu usuário!**

A aplicação está configurada para usar as variáveis `UID` e `GID` do arquivo `.env`, evitando que os arquivos sejam criados como root.

**Se você está tendo problemas com permissões ou loop de restart**, veja a seção [Container em loop de restart](#container-em-loop-de-restart-problema-de-permissões) acima.

---

## Segurança

### Recomendações importantes:

1. **Sempre altere a SECRET_KEY** no arquivo `.env`
2. **Use HTTPS** em produção (Nginx + Let's Encrypt)
3. **Configure firewall** para permitir apenas portas necessárias
4. **Backup regular** do banco de dados
5. **Atualize dependências** regularmente: `pip list --outdated`

### Configurar Firewall (UFW)

```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP e HTTPS (se usar Nginx)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Se NÃO usar Nginx, permitir porta 5000
sudo ufw allow 5000/tcp

# Ativar firewall
sudo ufw enable
```

---

## Atualizar a aplicação

```bash
# 1. Fazer backup
cp data/tarefas.db data/backup.db

# 2. Parar aplicação
docker-compose down

# 3. Atualizar código (git pull ou upload de arquivos)
git pull  # se usar git

# 4. Rebuild e reiniciar
docker-compose build
docker-compose up -d

# 5. Verificar logs
docker-compose logs -f
```

---

## Monitoramento

### Ver uso de recursos

```bash
docker stats
```

### Auto-restart em caso de falha

Já configurado no `docker-compose.yml`:
```yaml
restart: unless-stopped
```

---

## Suporte

Criado com Flask, Jinja2 e muito amor!

Para dúvidas, consulte a documentação oficial:
- [Flask](https://flask.palletsprojects.com/)
- [Docker](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
