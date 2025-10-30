import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from datetime import datetime
from models import db, User, Tarefa

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
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validações
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
        elif password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
        elif len(password) < 6:
            flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Este usuário já existe.', 'danger')
        else:
            # Criar novo usuário
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))

    return render_template('registro.html')


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
    # Buscar apenas tarefas do usuário logado
    tarefas = Tarefa.query.filter_by(user_id=current_user.id).order_by(Tarefa.data).all()
    return render_template('index.html', tarefas=tarefas)


@app.route('/adicionar', methods=['POST'])
@login_required
def adicionar():
    data_str = request.form.get('data')
    descricao = request.form.get('descricao')

    if not data_str or not descricao:
        flash('Por favor, preencha todos os campos.', 'danger')
        return redirect(url_for('index'))

    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Data inválida.', 'danger')
        return redirect(url_for('index'))

    tarefa = Tarefa(
        data=data,
        descricao=descricao,
        user_id=current_user.id
    )
    db.session.add(tarefa)
    db.session.commit()

    flash('Tarefa adicionada com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    tarefa = Tarefa.query.get_or_404(id)

    # Verificar se a tarefa pertence ao usuário
    if tarefa.user_id != current_user.id:
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

    # Verificar se a tarefa pertence ao usuário
    if tarefa.user_id != current_user.id:
        flash('Você não tem permissão para deletar esta tarefa.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(tarefa)
    db.session.commit()
    flash('Tarefa deletada com sucesso!', 'success')
    return redirect(url_for('index'))


# ============= INICIALIZAÇÃO =============

def init_db():
    """Cria as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado!")


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
