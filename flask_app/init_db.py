#!/usr/bin/env python3
"""
Script para inicializar o banco de dados
Execute: python init_db.py
"""

import os
from app import app, db

def init_database():
    """Cria as tabelas do banco de dados"""
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("✓ Banco de dados inicializado com sucesso!")
        print(f"✓ Arquivo: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    init_database()
