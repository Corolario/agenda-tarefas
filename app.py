import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from datetime import datetime
from functools import wraps
from models import db, User, Tarefa, TaskGroup, user_taskgroup
from collections import defaultdict

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tarefas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============= DECORADORES =============

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ============= ROTAS DE AUTENTICAÇÃO =============

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('login'))


# ============= ROTAS DE TAREFAS =============

@app.route('/')
@login_required
def index():
    # Buscar grupos do usuário
    user_groups = current_user.task_groups

    # Se o usuário não pertence a nenhum grupo, retornar vazio
    if not user_groups:
        return render_template('index.html', tarefas_agrupadas=[], total_tarefas=0, user_groups=user_groups,
                             members_list=[], selected_user_id=None, selected_group_id=None)

    # Buscar IDs dos grupos do usuário
    group_ids = [group.id for group in user_groups]

    # Obter filtros da query string
    selected_user_id = request.args.get('user_id', type=int)
    selected_group_id = request.args.get('group_id', type=int)

    # Buscar todas as tarefas dos grupos que o usuário pertence
    query = Tarefa.query.filter(Tarefa.task_group_id.in_(group_ids))

    # Aplicar filtro de grupo se selecionado
    if selected_group_id:
        # Verificar se o usuário pertence a este grupo
        if selected_group_id in group_ids:
            query = query.filter(Tarefa.task_group_id == selected_group_id)

    # Aplicar filtro de usuário se selecionado
    if selected_user_id:
        query = query.filter(Tarefa.user_id == selected_user_id)

    tarefas = query.order_by(Tarefa.data).all()

    # Buscar todos os membros dos grupos para o filtro
    members_set = set()
    if selected_group_id:
        # Se um grupo está selecionado, mostrar apenas membros daquele grupo
        selected_group = TaskGroup.query.get(selected_group_id)
        if selected_group:
            for member in selected_group.members.all():
                members_set.add((member.id, member.username))
    else:
        # Mostrar todos os membros de todos os grupos do usuário
        for group in user_groups:
            for member in group.members.all():
                members_set.add((member.id, member.username))
    members_list = sorted(list(members_set), key=lambda x: x[1])  # Ordenar por nome

    # Agrupar tarefas por mês/ano
    tarefas_por_mes = defaultdict(list)
    meses_ordem = []

    # Nomes dos meses em português
    meses_nomes = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    for tarefa in tarefas:
        mes_ano = (tarefa.data.year, tarefa.data.month)
        if mes_ano not in tarefas_por_mes:
            meses_ordem.append(mes_ano)
        tarefas_por_mes[mes_ano].append(tarefa)

    # Criar lista formatada de meses com suas tarefas
    tarefas_agrupadas = []
    for ano, mes in meses_ordem:
        mes_nome = f"{meses_nomes[mes]} de {ano}"
        tarefas_agrupadas.append({
            'mes_nome': mes_nome,
            'tarefas': tarefas_por_mes[(ano, mes)]
        })

    return render_template('index.html', tarefas_agrupadas=tarefas_agrupadas, total_tarefas=len(tarefas),
                         user_groups=user_groups, members_list=members_list,
                         selected_user_id=selected_user_id, selected_group_id=selected_group_id)


@app.route('/adicionar', methods=['POST'])
@login_required
def adicionar():
    data_str = request.form.get('data')
    descricao = request.form.get('descricao')
    task_group_id = request.form.get('task_group_id')

    if not data_str or not descricao or not task_group_id:
        flash('Por favor, preencha todos os campos.', 'danger')
        return redirect(url_for('index'))

    # Verificar se o usuário pertence ao grupo
    task_group = TaskGroup.query.get(task_group_id)
    if not task_group or task_group not in current_user.task_groups:
        flash('Você não pertence a este grupo de tarefas.', 'danger')
        return redirect(url_for('index'))

    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Data inválida.', 'danger')
        return redirect(url_for('index'))

    tarefa = Tarefa(
        data=data,
        descricao=descricao,
        user_id=current_user.id,
        task_group_id=task_group_id
    )
    db.session.add(tarefa)
    db.session.commit()

    flash('Tarefa adicionada com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    tarefa = Tarefa.query.get_or_404(id)

    # Verificar permissões
    # Admin pode editar qualquer tarefa do grupo
    # Usuário comum só pode editar suas próprias tarefas
    task_group = tarefa.task_group
    if task_group not in current_user.task_groups:
        flash('Você não tem permissão para editar esta tarefa.', 'danger')
        return redirect(url_for('index'))

    if not current_user.is_admin and tarefa.user_id != current_user.id:
        flash('Você não tem permissão para editar esta tarefa.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        data_str = request.form.get('data')
        descricao = request.form.get('descricao')

        if not data_str or not descricao:
            flash('Por favor, preencha todos os campos.', 'danger')
        else:
            try:
                tarefa.data = datetime.strptime(data_str, '%Y-%m-%d').date()
                tarefa.descricao = descricao
                db.session.commit()
                flash('Tarefa atualizada com sucesso!', 'success')
                return redirect(url_for('index'))
            except ValueError:
                flash('Data inválida.', 'danger')

    return render_template('editar.html', tarefa=tarefa)


@app.route('/deletar/<int:id>', methods=['POST'])
@login_required
def deletar(id):
    tarefa = Tarefa.query.get_or_404(id)

    # Verificar permissões
    # Admin pode deletar qualquer tarefa do grupo
    # Usuário comum só pode deletar suas próprias tarefas
    task_group = tarefa.task_group
    if task_group not in current_user.task_groups:
        flash('Você não tem permissão para deletar esta tarefa.', 'danger')
        return redirect(url_for('index'))

    if not current_user.is_admin and tarefa.user_id != current_user.id:
        flash('Você não tem permissão para deletar esta tarefa.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(tarefa)
    db.session.commit()
    flash('Tarefa deletada com sucesso!', 'success')
    return redirect(url_for('index'))


# ============= ROTAS DE ADMINISTRAÇÃO =============

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Dashboard de administração"""
    groups = TaskGroup.query.filter_by(admin_id=current_user.id).all()
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/dashboard.html', groups=groups, users=users)


@app.route('/admin/groups/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_group():
    """Criar novo grupo de tarefas"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Por favor, preencha o nome do grupo.', 'danger')
        else:
            group = TaskGroup(
                name=name,
                description=description,
                admin_id=current_user.id
            )
            db.session.add(group)
            db.session.commit()
            flash(f'Grupo "{name}" criado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin/create_group.html')


@app.route('/admin/groups/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_group(id):
    """Editar grupo de tarefas"""
    group = TaskGroup.query.get_or_404(id)

    # Verificar se o grupo pertence ao admin
    if group.admin_id != current_user.id:
        flash('Você não tem permissão para editar este grupo.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Por favor, preencha o nome do grupo.', 'danger')
        else:
            group.name = name
            group.description = description
            db.session.commit()
            flash(f'Grupo "{name}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_group.html', group=group)


@app.route('/admin/groups/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_group(id):
    """Deletar grupo de tarefas"""
    group = TaskGroup.query.get_or_404(id)

    # Verificar se o grupo pertence ao admin
    if group.admin_id != current_user.id:
        flash('Você não tem permissão para deletar este grupo.', 'danger')
        return redirect(url_for('admin_dashboard'))

    group_name = group.name
    db.session.delete(group)
    db.session.commit()
    flash(f'Grupo "{group_name}" deletado com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/groups/<int:id>/members', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_group_members(id):
    """Gerenciar membros do grupo"""
    group = TaskGroup.query.get_or_404(id)

    # Verificar se o grupo pertence ao admin
    if group.admin_id != current_user.id:
        flash('Você não tem permissão para gerenciar este grupo.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')

        if not user_id:
            flash('Usuário não especificado.', 'danger')
            return redirect(url_for('admin_group_members', id=id))

        user = User.query.get(user_id)
        if not user:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('admin_group_members', id=id))

        if action == 'add':
            if user not in group.members.all():
                group.members.append(user)
                db.session.commit()
                flash(f'Usuário "{user.username}" adicionado ao grupo.', 'success')
            else:
                flash(f'Usuário "{user.username}" já está no grupo.', 'info')
        elif action == 'remove':
            if user in group.members.all():
                group.members.remove(user)
                db.session.commit()
                flash(f'Usuário "{user.username}" removido do grupo.', 'success')
            else:
                flash(f'Usuário "{user.username}" não está no grupo.', 'info')

        return redirect(url_for('admin_group_members', id=id))

    # Listar membros atuais e usuários disponíveis
    current_members = group.members.all()
    all_users = User.query.all()  # Incluir todos os usuários, inclusive admins
    available_users = [u for u in all_users if u not in current_members]

    return render_template('admin/group_members.html', group=group,
                         current_members=current_members,
                         available_users=available_users)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_user():
    """Criar novo usuário comum"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
        elif len(password) < 6:
            flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
        elif password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
        else:
            # Verificar se usuário já existe
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash(f'O usuário "{username}" já existe.', 'danger')
            else:
                user = User(username=username, is_admin=False)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash(f'Usuário "{username}" criado com sucesso!', 'success')
                return redirect(url_for('admin_dashboard'))

    return render_template('admin/create_user.html')


# ============= INICIALIZAÇÃO =============

def init_db():
    """Cria as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado!")


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
