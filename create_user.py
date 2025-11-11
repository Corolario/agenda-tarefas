#!/usr/bin/env python3
"""
Script para gerenciar usuários administradores do sistema de agenda.
Uso: python create_user.py
"""

from app import app, db
from models import User
import getpass
import sys

def list_admins():
    """Lista todos os usuários administradores"""
    print("\n=== Usuários Administradores ===\n")

    try:
        with app.app_context():
            admins = User.query.filter_by(is_admin=True).order_by(User.username).all()

            if not admins:
                print("Nenhum administrador cadastrado.\n")
                return

            print(f"{'Usuário':<20} {'Criado em':<25} {'ID':<10}")
            print("-" * 55)

            for admin in admins:
                created = admin.created_at.strftime('%d/%m/%Y às %H:%M')
                print(f"{admin.username:<20} {created:<25} {admin.id:<10}")

            print(f"\nTotal: {len(admins)} administrador(es)\n")

    except Exception as e:
        print(f"\n❌ Erro ao listar administradores: {e}\n")

def create_admin():
    """Cria um novo usuário administrador"""
    print("\n=== Criar Novo Administrador ===\n")

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

    # Criar administrador
    try:
        with app.app_context():
            user = User(username=username, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

        print(f"\n✅ Administrador '{username}' criado com sucesso!\n")
        return True

    except Exception as e:
        print(f"\n❌ Erro ao criar administrador: {e}\n")
        return False

def show_menu():
    """Exibe o menu principal"""
    print("\n" + "="*50)
    print("  GERENCIAMENTO DE ADMINISTRADORES")
    print("="*50)
    print("\n1. Criar novo administrador")
    print("2. Listar administradores")
    print("3. Sair")
    print("\n" + "-"*50)

def main():
    """Função principal com menu interativo"""
    while True:
        show_menu()

        try:
            choice = input("\nEscolha uma opção (1-3): ").strip()

            if choice == '1':
                create_admin()
            elif choice == '2':
                list_admins()
            elif choice == '3':
                print("\n👋 Até logo!\n")
                sys.exit(0)
            else:
                print("\n❌ Opção inválida. Por favor, escolha 1, 2 ou 3.\n")

        except KeyboardInterrupt:
            print("\n\n👋 Operação cancelada. Até logo!\n")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 Até logo!\n")
            sys.exit(0)

if __name__ == '__main__':
    main()
