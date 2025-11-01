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

# Criar diretório para banco de dados
RUN mkdir -p /app/data

# Expor porta
EXPOSE 5000

# Criar script de inicialização
RUN echo '#!/bin/bash\npython init_db.py\nexec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app' > /app/start.sh && \
    chmod +x /app/start.sh

# Comando para iniciar a aplicação
CMD ["/app/start.sh"]
