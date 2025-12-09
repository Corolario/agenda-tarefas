# Usar imagem oficial do Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Criar diretório para banco de dados e definir permissões
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 5000

# Comando para iniciar a aplicação
CMD python init_db.py && gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
