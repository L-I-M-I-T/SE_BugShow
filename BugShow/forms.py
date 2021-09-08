from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField, BooleanField, TextAreaField, FileField, Label, HiddenField, PasswordField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError
from models import *
from flask_ckeditor import CKEditorField

class BaseUserForm(FlaskForm):
    user_name = StringField(u'用户名',
                            validators=[DataRequired(message='用户名不能为空'),
                                        Length(min=1, max=16, message='用户名长度限定在1-16位之间'),
                                        Regexp('^[a-zA-Z0-9_]*$',
                                               message='用户名只能包含数字、字母以及下划线.')],
                            render_kw={'placeholder': '请输入用户名长度1-16之间'})
    nickname = StringField(u'昵称',
                           validators=[DataRequired(message='昵称不能为空'),
                                       Length(min=1, max=20, message='昵称长度限定在1-20位之间')],
                           render_kw={'placeholder': '请输入昵称长度1-20之间'})
    user_email = StringField(u'注册邮箱',
                             render_kw={'placeholder': '请输入注册邮箱', 'type': 'email'})

    submit = SubmitField(u'注册', render_kw={'class': 'btn btn-success btn-xs'})

class RegisterForm(FlaskForm):
    user_role = SelectField(label=u'用户角色',
                        default=1,
                        coerce=int)
    user_name = StringField(u'用户名',
                            validators=[DataRequired(message='用户名不能为空'),
                                        Length(min=1, max=16, message='用户名长度限定在1-16位之间'),
                                        Regexp('^[a-zA-Z0-9_]*$',
                                               message='用户名只能包含数字、字母以及下划线.')],
                            render_kw={'placeholder': '请输入用户名长度1-16之间'})
    nickname = StringField(u'昵称',
                           validators=[DataRequired(message='昵称不能为空'),
                                       Length(min=1, max=20, message='昵称长度限定在1-16位之间')],
                           render_kw={'placeholder': '请输入昵称长度1-20之间'})
    user_email = StringField(u'注册邮箱',
                             validators=[DataRequired(message='注册邮箱不能为空'),
                                         Length(min=4, message='注册邮箱长度必须大于4')],
                             render_kw={'placeholder': '请输入注册邮箱', 'type': 'email'})
    password = StringField(u'密码',
                           validators=[DataRequired(message='用户密码不能为空'),
                                       Length(min=8, max=40, message='用户密码长度限定在8-40位之间'),
                                       EqualTo('confirm_pwd', message='两次密码不一致')],
                           render_kw={'placeholder': '请输入密码', 'type': 'password'})
    confirm_pwd = StringField(u'确认密码',
                              validators=[DataRequired(message='用户密码不能为空'),
                                          Length(min=8, max=40, message='用户密码长度限定在8-40位之间')],
                              render_kw={'placeholder': '输入确认密码', 'type': 'password'})
    submit = SubmitField(u'注册', render_kw={'class': 'source-button btn btn-primary btn-xs mt-2'})

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        user_roles = Role.query.all()
        self.user_role.choices = [(role.id, role.name) for role in user_roles] 

    def validate_user_name(self, filed):
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError('用户名已被注册.')

    def validate_user_email(self, filed):
        if User.query.filter_by(email=filed.data.lower()).first():
            raise ValidationError('邮箱已被注册.')

    def validate_nickname(self, filed):
        if User.query.filter_by(nickname=filed.data).first():
            raise ValidationError('昵称已被注册')

class LoginForm(FlaskForm):
    usr_email = StringField(u'邮箱/用户名', validators=[DataRequired(message='用户名或邮箱不能为空')],
                            render_kw={'placeholder': '请输入邮箱或用户名'})
    password = StringField(u'登录密码',
                           validators=[DataRequired(message='登录密码不能为空'),
                                       Length(min=8, max=40, message='登录密码必须在8-40位之间')],
                           render_kw={'type': 'password', 'placeholder': '请输入用户密码'})
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录', render_kw={'class': 'source-button btn btn-primary btn-xs'})

class BasePostForm(FlaskForm):
    title = StringField(u'标题', validators=[DataRequired(message='标题不能为空'),
                                        Length(min=1, max=50, message='标题长度必须在1到50位之间')],
                        render_kw={'class': '', 'rows': 50, 'placeholder': '输入您的讨论标题'})
    problem = SelectField(label=u'所属问题',
                        default=1,
                        coerce=int)
    body = CKEditorField('讨论内容', validators=[DataRequired(message='请输入讨论内容')])
    submit = SubmitField(u'发布', render_kw={'class': 'source-button btn btn-primary btn-xs mt-2 text-right'})

    def __init__(self, *args, **kwargs):
        super(BasePostForm, self).__init__(*args, **kwargs)
        problems = Problem.query.all()
        self.problem.choices = [(pro.id, pro.name) for pro in problems] 

class CreatePostForm(BasePostForm):
    def validate_title(self, field):
         if Post.query.filter_by(title=field.data).first():
            raise ValidationError('该标题已存在请换一个!')

class CreateAnswerForm(BasePostForm):
    dt = DateTimeField(u'开放时间', default=datetime.datetime.now)
    def validate_title(self, field):
         if Post.query.filter_by(title=field.data).first():
            raise ValidationError('该标题已存在请换一个!')

class EditPostForm(BasePostForm):
    submit = SubmitField(u'保存编辑', render_kw={'class': 'source-button btn btn-danger btn-xs mt-2 text-right'})

class EditAnswerForm(BasePostForm):
    dt = DateTimeField(u'开放时间', default=datetime.datetime.now)
    submit = SubmitField(u'保存编辑', render_kw={'class': 'source-button btn btn-danger btn-xs mt-2 text-right'})

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password1 = PasswordField('新密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2', message='两次密码必须一致!')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    set = SubmitField(u'修改', render_kw={'class': 'btn btn-success'})

class ChangeAvatarForm(FlaskForm):
    image = FileField('头像', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], '头像文件类型必须为jpg或者png!')
    ])
    submit = SubmitField(u'确认', render_kw={'class': 'btn btn-success'})

class BaseNoticeForm(FlaskForm):
    title = StringField(u'标题', validators=[DataRequired(message='标题不能为空'),
                                        Length(min=1, max=20, message='标题长度必须在1到20位之间')],
                        render_kw={'class': '', 'rows': 20, 'placeholder': '输入您的消息标题'})
    body = CKEditorField('消息内容', validators=[DataRequired(message='请输入消息内容')])
    submit = SubmitField(u'发布', render_kw={'class': 'source-button btn btn-primary btn-xs mt-2 text-right'})

    def __init__(self, *args, **kwargs):
        super(BaseNoticeForm, self).__init__(*args, **kwargs)

class CreateNoticeForm(BaseNoticeForm):
    def validate_title(self, filed):
        if Notice.query.filter_by(title=filed.data).first():
            raise ValidationError('该标题已存在请换一个!')

class EditNoticeForm(BaseNoticeForm):
    submit = SubmitField(u'保存编辑', render_kw={'class': 'source-button btn btn-danger btn-xs mt-2 text-right'})
