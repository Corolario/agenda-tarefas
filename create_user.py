#!/usr/bin/env python3
"""
Script para criar novos usuários no sistema de agenda.
Uso: python create_user.py
"""

from app import app, db
from models import User
import getpass

def create_user():
    """Cria um novo usuário interativamente"""
    print("\n=== Criar Novo Usuário ===\n")

    # Solicitar username
    while True:
        username = input("Nome de usuário: ").strip()
        if not username:
            print("❌ O nome de usuário não pode ser vazio.")
            continue

        # Verificar se já existe
        with app.app_context():
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"❌ O usuário '{username}' já existe.")
                continue
        break

    # Solicitar senha
    while True:
        password = getpass.getpass("Senha (mínimo 6 caracteres): ")
        if len(password) < 6:
            print("❌ A senha deve ter no mínimo 6 caracteres.")
            continue

        confirm_password = getpass.getpass("Confirme a senha: ")
        if password != confirm_password:
            print("❌ As senhas não coincidem.")
            continue
        break

    # Solicitar se é administrador
    while True:
        is_admin_input = input("Este usuário é administrador? (s/n): ").strip().lower()
        if is_admin_input in ['s', 'n']:
            is_admin = is_admin_input == 's'
            break
        print("❌ Por favor, digite 's' para sim ou 'n' para não.")

    # Criar usuário
    try:
        with app.app_context():
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

        user_type = "administrador" if is_admin else "comum"
        print(f"\n✅ Usuário '{username}' ({user_type}) criado com sucesso!\n")
        return True

    except Exception as e:
        print(f"\n❌ Erro ao criar usuário: {e}\n")
        return False

if __name__ == '__main__':
    create_user()
