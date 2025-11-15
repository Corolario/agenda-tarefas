from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime

db = SQLAlchemy()

# Inicializar Argon2 Password Hasher
# Argon2id é a variante recomendada que combina resistência a ataques de tempo e memória
ph = PasswordHasher()

# Tabela associativa para relacionamento many-to-many entre User e TaskGroup
user_taskgroup = db.Table('user_taskgroup',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('taskgroup_id', db.Integer, db.ForeignKey('task_groups.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento com tarefas
    tarefas = db.relationship('Tarefa', backref='usuario', lazy=True, cascade='all, delete-orphan')

    # Relacionamento many-to-many com grupos de tarefas
    task_groups = db.relationship('TaskGroup', secondary=user_taskgroup, backref=db.backref('members', lazy='dynamic'))

    def set_password(self, password):
        """
        Cria hash da senha usando Argon2id.
        Argon2 é o vencedor do Password Hashing Competition e oferece
        melhor proteção contra ataques de força bruta e rainbow tables.
        """
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta usando Argon2."""
        try:
            ph.verify(self.password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    def __repr__(self):
        return f'<User {self.username}>'


class TaskGroup(db.Model):
    __tablename__ = 'task_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relacionamento com o administrador do grupo
    admin = db.relationship('User', foreign_keys=[admin_id], backref='administered_groups')

    # Relacionamento com tarefas
    tarefas = db.relationship('Tarefa', backref='task_group', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TaskGroup {self.name}>'


class Tarefa(db.Model):
    __tablename__ = 'tarefas'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_group_id = db.Column(db.Integer, db.ForeignKey('task_groups.id'), nullable=False)

    def __repr__(self):
        return f'<Tarefa {self.id}: {self.data}>'
