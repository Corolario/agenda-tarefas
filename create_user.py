#!/usr/bin/env python3
"""
Script para gerenciar usuários do sistema de agenda.
Funcionalidades:
- Criar novos administradores
- Listar administradores
- Listar todos os usuários
- Alterar senha de usuários (administradores e normais)
- Deletar usuários (administradores e normais)

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

def list_all_users():
    """Lista todos os usuários do sistema (administradores e normais)"""
    print("\n=== Todos os Usuários ===\n")

    try:
        with app.app_context():
            users = User.query.order_by(User.username).all()

            if not users:
                print("Nenhum usuário cadastrado.\n")
                return

            print(f"{'Usuário':<20} {'Tipo':<15} {'Criado em':<25} {'ID':<10}")
            print("-" * 70)

            for user in users:
                created = user.created_at.strftime('%d/%m/%Y às %H:%M')
                user_type = "Administrador" if user.is_admin else "Usuário"
                print(f"{user.username:<20} {user_type:<15} {created:<25} {user.id:<10}")

            admin_count = sum(1 for u in users if u.is_admin)
            normal_count = len(users) - admin_count
            print(f"\nTotal: {len(users)} usuário(s) ({admin_count} admin(s), {normal_count} normal(is))\n")

    except Exception as e:
        print(f"\n❌ Erro ao listar usuários: {e}\n")

def change_password():
    """Altera a senha de um usuário existente"""
    print("\n=== Alterar Senha de Usuário ===\n")

    try:
        with app.app_context():
            # Listar todos os usuários
            users = User.query.order_by(User.username).all()

            if not users:
                print("Nenhum usuário cadastrado.\n")
                return False

            print(f"{'#':<5} {'Usuário':<20} {'Tipo':<15}")
            print("-" * 40)

            for idx, user in enumerate(users, 1):
                user_type = "Administrador" if user.is_admin else "Usuário"
                print(f"{idx:<5} {user.username:<20} {user_type:<15}")

            print()

            # Solicitar seleção do usuário
            while True:
                try:
                    choice = input(f"Escolha o usuário (1-{len(users)}) ou 0 para cancelar: ").strip()
                    choice_num = int(choice)

                    if choice_num == 0:
                        print("\n❌ Operação cancelada.\n")
                        return False

                    if 1 <= choice_num <= len(users):
                        selected_user = users[choice_num - 1]
                        break
                    else:
                        print(f"❌ Por favor, escolha um número entre 1 e {len(users)}.")
                except ValueError:
                    print("❌ Por favor, digite um número válido.")

            # Confirmar usuário selecionado
            user_type = "administrador" if selected_user.is_admin else "usuário"
            print(f"\nUsuário selecionado: {selected_user.username} ({user_type})")

            # Solicitar nova senha
            while True:
                password = getpass.getpass("\nNova senha (mínimo 6 caracteres): ")
                if len(password) < 6:
                    print("❌ A senha deve ter no mínimo 6 caracteres.")
                    continue

                confirm_password = getpass.getpass("Confirme a nova senha: ")
                if password != confirm_password:
                    print("❌ As senhas não coincidem.")
                    continue
                break

            # Atualizar senha
            selected_user.set_password(password)
            db.session.commit()

            print(f"\n✅ Senha do usuário '{selected_user.username}' alterada com sucesso!\n")
            return True

    except Exception as e:
        print(f"\n❌ Erro ao alterar senha: {e}\n")
        return False

def delete_user():
    """Deleta um usuário do sistema (administrador ou normal)"""
    print("\n=== Deletar Usuário ===\n")

    try:
        with app.app_context():
            # Listar todos os usuários
            users = User.query.order_by(User.username).all()

            if not users:
                print("Nenhum usuário cadastrado.\n")
                return False

            print(f"{'#':<5} {'Usuário':<20} {'Tipo':<15} {'ID':<10}")
            print("-" * 50)

            for idx, user in enumerate(users, 1):
                user_type = "Administrador" if user.is_admin else "Usuário"
                print(f"{idx:<5} {user.username:<20} {user_type:<15} {user.id:<10}")

            print()

            # Solicitar seleção do usuário
            while True:
                try:
                    choice = input(f"Escolha o usuário a deletar (1-{len(users)}) ou 0 para cancelar: ").strip()
                    choice_num = int(choice)

                    if choice_num == 0:
                        print("\n❌ Operação cancelada.\n")
                        return False

                    if 1 <= choice_num <= len(users):
                        selected_user = users[choice_num - 1]
                        break
                    else:
                        print(f"❌ Por favor, escolha um número entre 1 e {len(users)}.")
                except ValueError:
                    print("❌ Por favor, digite um número válido.")

            # Verificar se é o último administrador
            if selected_user.is_admin:
                admin_count = User.query.filter_by(is_admin=True).count()
                if admin_count <= 1:
                    print("\n❌ Não é possível deletar o único administrador do sistema.\n")
                    return False

            # Confirmar deleção
            user_type = "administrador" if selected_user.is_admin else "usuário"
            print(f"\n⚠️  ATENÇÃO: Você está prestes a deletar o {user_type} '{selected_user.username}'.")
            print("Esta ação NÃO pode ser desfeita e todas as tarefas associadas a este usuário também serão deletadas.\n")

            confirmation = input("Digite 'DELETAR' para confirmar: ").strip()

            if confirmation != 'DELETAR':
                print("\n❌ Operação cancelada (confirmação incorreta).\n")
                return False

            # Deletar usuário
            username = selected_user.username
            db.session.delete(selected_user)
            db.session.commit()

            print(f"\n✅ Usuário '{username}' deletado com sucesso!\n")
            return True

    except Exception as e:
        print(f"\n❌ Erro ao deletar usuário: {e}\n")
        db.session.rollback()
        return False

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
    print("  GERENCIAMENTO DE USUÁRIOS")
    print("="*50)
    print("\n1. Criar novo administrador")
    print("2. Listar administradores")
    print("3. Listar todos os usuários")
    print("4. Alterar senha de usuário")
    print("5. Deletar usuário")
    print("6. Sair")
    print("\n" + "-"*50)

def main():
    """Função principal com menu interativo"""
    while True:
        show_menu()

        try:
            choice = input("\nEscolha uma opção (1-6): ").strip()

            if choice == '1':
                create_admin()
            elif choice == '2':
                list_admins()
            elif choice == '3':
                list_all_users()
            elif choice == '4':
                change_password()
            elif choice == '5':
                delete_user()
            elif choice == '6':
                print("\n👋 Até logo!\n")
                sys.exit(0)
            else:
                print("\n❌ Opção inválida. Por favor, escolha 1, 2, 3, 4, 5 ou 6.\n")

        except KeyboardInterrupt:
            print("\n\n👋 Operação cancelada. Até logo!\n")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 Até logo!\n")
            sys.exit(0)

if __name__ == '__main__':
    main()
