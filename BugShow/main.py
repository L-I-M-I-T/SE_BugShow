from flask import render_template
from flask import Flask
from flask_login import LoginManager,login_user
from settings import DevelopmentConfig
from flask_sqlalchemy import SQLAlchemy
from blueprint.index import index_bp
from blueprint.auth import auth_bp
from blueprint.notice import notice_bp
from blueprint.normal import normal_bp
from blueprint.post import post_bp
from extensions import *
from models import *
import pymysql
from flask_bootstrap import Bootstrap
import click

pymysql.install_as_MySQLdb()
app = Flask(__name__)

def init_db(db):
    db.drop_all()
    click.echo('清空数据库完成!')
    db.create_all()
    init_problem(db)
    init_role(db)

# 初始化问题表，此处生成一些已有的问题
def init_problem(db):
    r1 = Problem(name="软件架构与设计模式", id=1)
    r2 = Problem(name="语法制导的语义分析", id=2)
    r3 = Problem(name="进程通信的7种基本方式", id=3)
    r4 = Problem(name="红黑树的插入和删除", id=4)
    r5 = Problem(name="无向图的最大割问题", id=5)
    r6 = Problem(name="SQL语句的使用-入门", id=6)
    r7 = Problem(name="SQL语句的使用-进阶", id=7)
    r8 = Problem(name="基于K-means的图像分割", id=8)
    r9 = Problem(name="Mask-RCNN在Deepfake方向的基本应用", id=9)
    r10 = Problem(name="上下文无关语法", id=10)
    db.session.add(r1)
    db.session.add(r2)
    db.session.add(r3)
    db.session.add(r4)
    db.session.add(r5)
    db.session.add(r6)
    db.session.add(r7)
    db.session.add(r8)
    db.session.add(r9)
    db.session.add(r10)
    db.session.commit()

# 初始化角色表，生成三种相应的角色
def init_role(db):
    r1 = Role(name="学生")
    r2 = Role(name="老师")
    r3 = Role(name="管理员")
    db.session.add(r1)
    db.session.add(r2)
    db.session.add(r3)
    db.session.commit()

if __name__ == '__main__':
    app.jinja_env.add_extension('jinja2.ext.do')
    app.config.from_object(DevelopmentConfig)
    
    db.init_app(app)
    # 对数据库进行初始化操作，打开/关闭注释以在运行项目时启动/禁用该操作
    # with app.app_context():
    #     init_db(db)
    bootstrap = Bootstrap(app)
    login_manager.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    moment.init_app(app)
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(normal_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(notice_bp)
    print(app.url_map)
    app.run(host='0.0.0.0',port=8080)
