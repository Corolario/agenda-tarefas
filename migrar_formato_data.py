# -*- coding: utf-8 -*-
"""
Script de migração do banco de dados tarefas.db
Converte o formato de data de DD/MM/YYYY para YYYY-MM-DD
"""
import sqlite3
from datetime import datetime


def migrar_formato_data():
    """Migra o formato de data de DD/MM/YYYY para YYYY-MM-DD"""

    print("🔄 Iniciando migração do formato de data...")

    try:
        # Conectar ao banco
        conn = sqlite3.connect('tarefas.db')
        c = conn.cursor()

        # Buscar todas as tarefas
        c.execute('SELECT id, data FROM tarefas')
        tarefas = c.fetchall()

        print(f"📊 Encontradas {len(tarefas)} tarefas para migrar")

        # Contador de sucesso e erros
        sucesso = 0
        erros = 0

        # Migrar cada tarefa
        for id_tarefa, data_antiga in tarefas:
            try:
                # Tentar converter DD/MM/YYYY para YYYY-MM-DD
                data_obj = datetime.strptime(data_antiga, '%d/%m/%Y')
                data_nova = data_obj.strftime('%Y-%m-%d')

                # Atualizar no banco
                c.execute('UPDATE tarefas SET data = ? WHERE id = ?', (data_nova, id_tarefa))

                print(f"  ✓ ID {id_tarefa}: {data_antiga} → {data_nova}")
                sucesso += 1

            except ValueError as e:
                print(f"  ✗ ID {id_tarefa}: Erro ao converter '{data_antiga}' - {e}")
                erros += 1

        # Commit das mudanças
        conn.commit()
        conn.close()

        print(f"\n✅ Migração concluída!")
        print(f"   Sucesso: {sucesso}")
        print(f"   Erros: {erros}")

        if erros == 0:
            print("\n🎉 Todas as datas foram migradas com sucesso!")
        else:
            print(f"\n⚠️  Atenção: {erros} registro(s) não foram migrados")

    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        return False

    return True


def fazer_backup():
    """Cria um backup do banco antes da migração"""
    import shutil
    from datetime import datetime

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'tarefas_backup_{timestamp}.db'

    try:
        shutil.copy('tarefas.db', backup_name)
        print(f"💾 Backup criado: {backup_name}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False


if __name__ == '__main__':
    print("="*60)
    print("  MIGRAÇÃO DE FORMATO DE DATA - TAREFAS.DB")
    print("  De: DD/MM/YYYY  →  Para: YYYY-MM-DD")
    print("="*60)
    print()

    # Perguntar se quer fazer backup
    resposta = input("Deseja fazer backup do banco antes da migração? (s/n): ")

    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        if not fazer_backup():
            print("Migração cancelada devido a erro no backup.")
            exit(1)
        print()

    # Confirmar migração
    resposta = input("Confirma a migração? (s/n): ")

    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        migrar_formato_data()
    else:
        print("❌ Migração cancelada pelo usuário.")
