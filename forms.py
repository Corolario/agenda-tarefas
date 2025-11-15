"""
Formulários da aplicação usando Flask-WTF para proteção CSRF e validação.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User


class LoginForm(FlaskForm):
    """Formulário de login"""
    username = StringField('Usuário', validators=[
        DataRequired(message='O nome de usuário é obrigatório.')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='A senha é obrigatória.')
    ])


class CreateUserForm(FlaskForm):
    """Formulário para criação de usuários"""
    username = StringField('Nome de usuário', validators=[
        DataRequired(message='O nome de usuário é obrigatório.'),
        Length(min=3, max=80, message='O nome de usuário deve ter entre 3 e 80 caracteres.')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='A senha é obrigatória.'),
        Length(min=6, message='A senha deve ter no mínimo 6 caracteres.')
    ])
    confirm_password = PasswordField('Confirme a senha', validators=[
        DataRequired(message='A confirmação de senha é obrigatória.'),
        EqualTo('password', message='As senhas não coincidem.')
    ])

    def validate_username(self, field):
        """Valida se o nome de usuário já existe"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(f'O usuário "{field.data}" já existe.')


class TaskForm(FlaskForm):
    """Formulário para adicionar tarefas"""
    data = DateField('Data', validators=[
        DataRequired(message='A data é obrigatória.')
    ], format='%Y-%m-%d')
    descricao = TextAreaField('Descrição', validators=[
        DataRequired(message='A descrição é obrigatória.'),
        Length(min=1, max=1000, message='A descrição deve ter no máximo 1000 caracteres.')
    ])
    task_group_id = SelectField('Grupo de Tarefas', validators=[
        DataRequired(message='Selecione um grupo de tarefas.')
    ], coerce=int)


class EditTaskForm(FlaskForm):
    """Formulário para editar tarefas"""
    data = DateField('Data', validators=[
        DataRequired(message='A data é obrigatória.')
    ], format='%Y-%m-%d')
    descricao = TextAreaField('Descrição', validators=[
        DataRequired(message='A descrição é obrigatória.'),
        Length(min=1, max=1000, message='A descrição deve ter no máximo 1000 caracteres.')
    ])


class TaskGroupForm(FlaskForm):
    """Formulário para criar/editar grupos de tarefas"""
    name = StringField('Nome do Grupo', validators=[
        DataRequired(message='O nome do grupo é obrigatório.'),
        Length(min=3, max=120, message='O nome deve ter entre 3 e 120 caracteres.')
    ])
    description = TextAreaField('Descrição', validators=[
        Length(max=500, message='A descrição deve ter no máximo 500 caracteres.')
    ])


class DeleteForm(FlaskForm):
    """Formulário simples para operações de delete (apenas CSRF)"""
    pass


class ManageMemberForm(FlaskForm):
    """Formulário para adicionar/remover membros de grupos"""
    action = HiddenField('Ação', validators=[DataRequired()])
    user_id = SelectField('Usuário', validators=[DataRequired()], coerce=int)
