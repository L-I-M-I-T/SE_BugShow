from flask import Blueprint, render_template
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import or_
from flask import flash
from extensions import db
from settings import BaseConfig
from models import *
from forms import *
from utils import *
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 获取表单中的参数
        role_id = form.user_role.data
        username = form.user_name.data
        nickname = form.nickname.data
        password = form.confirm_pwd.data
        email = form.user_email.data
        captcha = request.form.get('captcha')

        # 验证输入验证码和发往邮箱中的验证码是否一致
        code = VerifyCode.query.filter(VerifyCode.who == email, VerifyCode.is_work == 1).order_by(VerifyCode.timestamps.desc()).first()
        if code:
            if code.val != int(captcha):
                flash('验证码错误!', 'danger')
                return redirect(request.referrer)
            elif code.expire_time < datetime.datetime.now():
                flash('验证码已过期!', 'danger')
                return redirect(request.referrer)
        else:
            flash('请先发送验证码到邮箱!', 'info')
            return redirect(request.referrer)
        code.is_work = False

        # 注册成功，新增用户信息
        user = User(role_id=role_id, username=username, nickname=nickname, email=email, password=password)
        user.generate_avatar()
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('注册成功,欢迎加入BugShow!', 'success')
        return redirect(url_for('.login'))
    return render_template('register.html', template_folder='templates', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/'))
    form = LoginForm()
    if form.validate_on_submit():
        # 获取表单中的参数
        usr = form.usr_email.data
        pwd = form.password.data
        user = User.query.filter(or_(User.username == usr, User.email == usr.lower())).first()  # 可以使用账号名或邮箱进行登录

        # 验证账号和密码是否相符
        if user is not None and user.check_password(pwd):
            if login_user(user, form.remember_me.data):
                flash('登录成功!', 'success')
                return redirect(url_for('index_bp.index'))
        elif user is None:
            flash('无效的邮箱或用户名.', 'danger')
        else:
            flash('无效的密码', 'danger')
    return render_template('login.html', template_folder='templates', form=form)


@auth_bp.route('/change-passwd', methods=['GET', 'POST'])
@login_required
def ChangePassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 获取表单中的参数
        usr = current_user.id
        old_password = form.old_password.data
        passwd = form.password1.data
        user = User.query.filter(or_(User.id == usr)).first()

        # 验证旧密码是否正确，正确则进行密码修改
        if user.check_password(old_password):
            user.set_password(passwd)
            db.session.commit()
            flash('修改密码成功!', 'success')
            return redirect(url_for('index_bp.index'))
    return render_template('change-passwd.html', template_folder='templates', form=form)


@auth_bp.route('/change-avatar', methods=['GET', 'POST'])
@login_required
def ChangeAvatar():
    form = ChangeAvatarForm()
    if form.validate_on_submit():
        # 获取表单中的参数
        usr = current_user.id
        user = User.query.filter(or_(User.id == usr)).first()
        avatar = form.image.data

        # 将新上传的头像图片文件存储到对应路径下，并修改用户头像数据指向新文件
        upload_path = BaseConfig.AVATARS_SAVE_PATH + avatar.filename
        avatar.save(upload_path)
        user.set_avatar("resources/avatars/"+avatar.filename)
        db.session.commit()
        flash('修改头像成功!', 'success')
        return redirect(url_for('index_bp.index'))
    return render_template('change-avatar.html', template_folder='templates', form=form)


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('退出成功!', 'success')
    return redirect(url_for('index_bp.index'))
