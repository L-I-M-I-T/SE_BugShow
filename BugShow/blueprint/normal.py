from flask import Blueprint, send_from_directory, request, jsonify, current_app, render_template
from extensions import db, mail
from emails import send_email
from models import *
from utils import *
from settings import basedir, VERCODE_VALID_TIMESS
from flask_login import login_required
from flask_mail import Message
from threading import Thread
from time import thread_time
import datetime
import os

def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to_mail, subject, template, **kwargs):
    message = Message(current_app.config['BUGSHOW_MAIL_SUBJECT_PRE'] + subject, recipients=[to_mail], sender=current_app.config['MAIL_USERNAME'])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    # 新开线程单独进行发送邮件服务
    thread = Thread(target=async_send_mail, args=(current_app._get_current_object(), message))  
    thread.start()
    return thread

normal_bp = Blueprint('normal', __name__, url_prefix='/normal')

@normal_bp.route('/send-email', methods=['POST'])
def send():
    to_email = request.form.get('user_email')
    username = request.form.get('user_name')
    ver_code = generate_ver_code()
    send_email(to_mail=to_email, subject='Captcha', template='verifyCode', username=username, ver_code=ver_code)
    # 判断是否已经存在一个最新的可用的验证码,以确保生效的验证码是用户收到最新邮件中的验证码
    exist_code = VerifyCode.query.filter(VerifyCode.who == to_email, VerifyCode.is_work == 1).order_by(VerifyCode.timestamps.desc()).first()
    if exist_code:
        exist_code.is_work = False
    expire_time = datetime.datetime.now() + datetime.timedelta(minutes=VERCODE_VALID_TIME)
    verify_code = VerifyCode(value=ver_code, who=to_email, expire_time=expire_time)
    db.session.add(verify_code)
    db.session.commit()
    return jsonify({'tag': 1, 'info': '邮件发送成功!'})

@normal_bp.route('/image/upload/')
def image_upload():
    pass
