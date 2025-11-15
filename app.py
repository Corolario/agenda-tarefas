import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from dotenv import load_dotenv
from functools import wraps
from models import db, User, Tarefa, TaskGroup
from forms import (LoginForm, CreateUserForm, TaskForm, EditTaskForm,
                   TaskGroupForm, DeleteForm, ManageMemberForm)
from collections import defaultdict

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tarefas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de segurança
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'  # True em produção com HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Token CSRF não expira (usa session)
app.config['WTF_CSRF_SSL_STRICT'] = os.getenv('WTF_CSRF_SSL_STRICT', 'False') == 'True'  # True em produção

# Inicializar extensões
db.init_app(app)

# Proteção CSRF
csrf = CSRFProtect(app)

# Headers de segurança com Flask-Talisman (apenas em produção)
if os.getenv('FLASK_ENV') == 'production':
    # Content Security Policy
    csp = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",  # unsafe-inline necessário para scripts inline nos templates
        'style-src': "'self' 'unsafe-inline'",   # unsafe-inline necessário para estilos inline
        'img-src': "'self' data:",
        'font-src': "'self'",
    }
    Talisman(app,
             content_security_policy=csp,
             force_https=True,
             strict_transport_security=True,
             session_cookie_secure=True)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.session_protection = 'strong'  # Proteção adicional de sessão

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

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html', form=form)


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
    # Criar formulário de tarefa
    form = TaskForm()
    form.task_group_id.choices = [(g.id, g.name) for g in current_user.task_groups]

    # Buscar grupos do usuário
    user_groups = current_user.task_groups

    # Se o usuário não pertence a nenhum grupo, retornar vazio
    if not user_groups:
        return render_template('index.html', tarefas_agrupadas=[], total_tarefas=0, user_groups=user_groups,
                             members_list=[], selected_user_id=None, selected_group_id=None, form=form)

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
                         selected_user_id=selected_user_id, selected_group_id=selected_group_id, form=form)


@app.route('/adicionar', methods=['POST'])
@login_required
def adicionar():
    form = TaskForm()

    # Preencher choices do SelectField com grupos do usuário
    form.task_group_id.choices = [(g.id, g.name) for g in current_user.task_groups]

    if form.validate_on_submit():
        # Verificar se o usuário pertence ao grupo
        task_group = TaskGroup.query.get(form.task_group_id.data)
        if not task_group or task_group not in current_user.task_groups:
            flash('Você não pertence a este grupo de tarefas.', 'danger')
            return redirect(url_for('index'))

        tarefa = Tarefa(
            data=form.data.data,
            descricao=form.descricao.data,
            user_id=current_user.id,
            task_group_id=form.task_group_id.data
        )
        db.session.add(tarefa)
        db.session.commit()

        flash('Tarefa adicionada com sucesso!', 'success')
    else:
        # Mostrar erros de validação
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')

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

    form = EditTaskForm(obj=tarefa)

    if form.validate_on_submit():
        tarefa.data = form.data.data
        tarefa.descricao = form.descricao.data
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('editar.html', tarefa=tarefa, form=form)


@app.route('/deletar/<int:id>', methods=['POST'])
@login_required
def deletar(id):
    form = DeleteForm()

    if not form.validate_on_submit():
        flash('Token CSRF inválido.', 'danger')
        return redirect(url_for('index'))

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
    form = TaskGroupForm()

    if form.validate_on_submit():
        group = TaskGroup(
            name=form.name.data,
            description=form.description.data,
            admin_id=current_user.id
        )
        db.session.add(group)
        db.session.commit()
        flash(f'Grupo "{form.name.data}" criado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/create_group.html', form=form)


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

    form = TaskGroupForm(obj=group)

    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        db.session.commit()
        flash(f'Grupo "{form.name.data}" atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_group.html', group=group, form=form)


@app.route('/admin/groups/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_group(id):
    """Deletar grupo de tarefas"""
    form = DeleteForm()

    if not form.validate_on_submit():
        flash('Token CSRF inválido.', 'danger')
        return redirect(url_for('admin_dashboard'))

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

    form = ManageMemberForm()

    # Listar membros atuais e usuários disponíveis
    current_members = group.members.all()
    all_users = User.query.all()  # Incluir todos os usuários, inclusive admins

    if request.method == 'POST':
        # Preencher choices dinamicamente antes da validação
        action = request.form.get('action')
        if action == 'add':
            available_users = [u for u in all_users if u not in current_members]
            form.user_id.choices = [(u.id, u.username) for u in available_users]
        else:  # remove
            form.user_id.choices = [(u.id, u.username) for u in current_members]

        if form.validate_on_submit():
            user = User.query.get(form.user_id.data)
            if not user:
                flash('Usuário não encontrado.', 'danger')
                return redirect(url_for('admin_group_members', id=id))

            if form.action.data == 'add':
                if user not in current_members:
                    group.members.append(user)
                    db.session.commit()
                    flash(f'Usuário "{user.username}" adicionado ao grupo.', 'success')
                else:
                    flash(f'Usuário "{user.username}" já está no grupo.', 'info')
            elif form.action.data == 'remove':
                if user in current_members:
                    group.members.remove(user)
                    db.session.commit()
                    flash(f'Usuário "{user.username}" removido do grupo.', 'success')
                else:
                    flash(f'Usuário "{user.username}" não está no grupo.', 'info')

            return redirect(url_for('admin_group_members', id=id))

    # Para GET, preparar choices para ambos os formulários
    available_users = [u for u in all_users if u not in current_members]

    return render_template('admin/group_members.html', group=group,
                         current_members=current_members,
                         available_users=available_users, form=form)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_user():
    """Criar novo usuário comum"""
    form = CreateUserForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, is_admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Usuário "{form.username.data}" criado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/create_user.html', form=form)


# ============= INICIALIZAÇÃO =============

def init_db():
    """Cria as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado!")


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
