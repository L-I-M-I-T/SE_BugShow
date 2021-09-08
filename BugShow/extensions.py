from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment

# 创建相关扩展元件的实例

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
ckeditor = CKEditor()
moment = Moment()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    user = User.query.filter_by(id=user_id).first()
    return user

login_manager.login_view = 'auth.login'
login_manager.login_message = u'请先登陆!'
login_manager.login_message_category = 'danger'
