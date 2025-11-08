#!/usr/bin/env python3
"""
Script para migrar o banco de dados existente para o novo schema com grupos.
ATENÇÃO: Este script irá recriar o banco de dados. Faça backup antes de executar!

Uso: python migrate_db.py
"""

from app import app, db
from models import User, Tarefa, TaskGroup
import os

def migrate_database():
    """Migra o banco de dados para o novo schema"""
    print("\n=== Migração do Banco de Dados ===\n")

    db_path = 'tarefas.db'
    backup_path = 'tarefas.db.backup'

    # Verificar se existe banco antigo
    if os.path.exists(db_path):
        response = input(f"⚠️  O banco de dados '{db_path}' será recriado. Deseja continuar? (s/n): ").strip().lower()
        if response != 's':
            print("❌ Migração cancelada.")
            return False

        # Fazer backup
        print(f"📦 Criando backup em '{backup_path}'...")
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ Backup criado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            print("⚠️  Continuando sem backup...")

    print("\n🔄 Recriando banco de dados com novo schema...")

    try:
        with app.app_context():
            # Dropar todas as tabelas
            db.drop_all()
            print("✅ Tabelas antigas removidas")

            # Criar novas tabelas
            db.create_all()
            print("✅ Novas tabelas criadas")

            print("\n📊 Estrutura do banco de dados:")
            print("  - users (com campo is_admin)")
            print("  - task_groups")
            print("  - user_taskgroup (tabela associativa)")
            print("  - tarefas (com campo task_group_id)")

        print("\n✅ Migração concluída com sucesso!\n")
        print("📝 Próximos passos:")
        print("  1. Execute: python create_user.py")
        print("  2. Crie um usuário administrador")
        print("  3. Acesse a aplicação e crie grupos de tarefas")
        print("  4. Adicione usuários aos grupos")
        print(f"\n💡 Backup salvo em: {backup_path}\n")

        return True

    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}\n")
        return False

if __name__ == '__main__':
    migrate_database()
