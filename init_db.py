#!/usr/bin/env python3
"""
Script para inicializar o banco de dados
Execute: python init_db.py
"""

import os
import sys
from app import app, db

def init_database():
    """Cria as tabelas do banco de dados"""
    try:
        with app.app_context():
            # Criar todas as tabelas (não faz nada se já existirem)
            db.create_all()
            print("✓ Banco de dados inicializado com sucesso!")
            print(f"✓ Arquivo: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"✗ Erro ao inicializar banco de dados: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    init_database()
