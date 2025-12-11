#!/bin/bash
# Script para corrigir permissões do diretório data/ e configurar variáveis de ambiente

echo "=== Script de Correção de Permissões ==="
echo ""

# 1. Corrigir permissões do diretório data/ se existir
if [ -d "data" ]; then
    echo "📁 Diretório data/ encontrado. Verificando permissões..."

    # Verificar se o diretório pertence ao root
    if [ "$(stat -c '%U' data)" = "root" ]; then
        echo "⚠️  Diretório data/ pertence ao root. Corrigindo permissões..."
        sudo chown -R $USER:$USER data/
        echo "✅ Permissões corrigidas!"
    else
        echo "✅ Permissões já estão corretas."
    fi
else
    echo "📁 Criando diretório data/..."
    mkdir -p data
    echo "✅ Diretório criado!"
fi

echo ""

# 2. Configurar variáveis UID e GID no .env
if [ ! -f ".env" ]; then
    echo "📝 Arquivo .env não encontrado. Criando a partir de .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Arquivo .env criado!"
    else
        echo "⚠️  Arquivo .env.example não encontrado. Criando .env básico..."
        cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:////app/data/tarefas.db
FLASK_ENV=production
UID=$(id -u)
GID=$(id -g)
EOF
        echo "✅ Arquivo .env criado com SECRET_KEY aleatória!"
    fi
fi

# 3. Garantir que UID e GID estão no .env
if ! grep -q "^UID=" .env; then
    echo ""
    echo "📝 Adicionando UID e GID ao arquivo .env..."
    echo "" >> .env
    echo "# Permissões do Docker (para evitar arquivos criados como root)" >> .env
    echo "UID=$(id -u)" >> .env
    echo "GID=$(id -g)" >> .env
    echo "✅ UID e GID adicionados!"
else
    echo "✅ UID e GID já estão configurados no .env"
fi

echo ""
echo "=== Configuração completa! ==="
echo ""
echo "Seus valores:"
echo "  UID: $(id -u)"
echo "  GID: $(id -g)"
echo ""
echo "Próximos passos:"
echo "  1. docker-compose down (se estiver rodando)"
echo "  2. docker-compose build"
echo "  3. docker-compose up -d"
echo ""
