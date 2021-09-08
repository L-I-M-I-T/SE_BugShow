from flask import Blueprint, render_template, request, current_app, flash, redirect ,url_for
from models import *
import time
from flask_login import login_required, current_user
from extensions import db
from sqlalchemy.sql.expression import func
from sqlalchemy import and_, or_
index_bp = Blueprint('index_bp', __name__)

@index_bp.route('/')
@index_bp.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    tag = (Post.query.count() > current_app.config['PER_PAGE']) # 若查询结果多于每页最多显示条数，则需要进行分页显示
    problems = Problem.query.all()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    page = request.args.get('page', 1, type=int)
    # 学生只能查看超过ddl的问题的标准回答帖子，教师和管理员无此限制
    if (current_user.role.name == "学生"):
        pagination = Post.query.filter(Post.display_time < now).order_by(Post.update_time.desc()).paginate(page, per_page=current_app.config['PER_PAGE'])
    else:
        pagination = Post.query.order_by(Post.update_time.desc()).paginate(page, per_page=current_app.config['PER_PAGE'])
    latest = pagination.items
    return render_template('index.html', template_folder='templates', latest=latest, pagination=pagination, tag=tag, problems=problems, pro_id=0)

@index_bp.route('/index/newPro', methods=['POST', 'GET'])
def new_pro():
    name = request.form.get("name")
    # 不能创建相同的题目
    if Problem.query.filter_by(name=name).first():
        flash("该题目已存在",'danger')
    else :
        newpro = Problem(id=None, name=name)
        db.session.add(newpro)
        db.session.commit()
    return redirect(url_for('.index'))

@index_bp.route('/index/<pro_id>')
@index_bp.route('/index/lastupdate/<pro_id>')
@login_required
# 按最后更新时间降序排列显示帖子
def indexpro_lastupdate(pro_id):
    tag = (Post.query.filter_by(pro_id=pro_id).count() > current_app.config['PER_PAGE'])    # 若查询结果多于每页最多显示条数，则需要进行分页显示
    problems = Problem.query.all()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    page = request.args.get('page', 1, type=int)
    # 学生只能查看超过ddl的问题的标准回答帖子，教师和管理员无此限制
    if (current_user.role.name == "学生"):
        pagination = Post.query.filter(and_(Post.pro_id==pro_id, Post.display_time < now)).order_by(Post.star.desc(), Post.update_time.desc()).paginate(page, per_page=current_app.config['PER_PAGE']) 
    else:
        pagination = Post.query.filter(Post.pro_id==pro_id).order_by(Post.star.desc(), Post.update_time.desc()).paginate(page, per_page=current_app.config['PER_PAGE'])  
    latest = pagination.items
    problem = Problem.query.filter_by(id=pro_id).first()
    return render_template('index.html', template_folder='templates', latest=latest, pagination=pagination, tag=tag, problems=problems, pro_id=pro_id,name=problem.name, mod="lastupdate")


@index_bp.route('/index/lastcreate/<pro_id>')
@login_required
# 按创建时间降序排列显示帖子
def indexpro_lastcreate(pro_id):
    tag = (Post.query.filter_by(pro_id=pro_id).count() > current_app.config['PER_PAGE'])    # 若查询结果多于每页最多显示条数，则需要进行分页显示
    problems = Problem.query.all()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    page = request.args.get('page', 1, type=int)
    # 学生只能查看超过ddl的问题的标准回答帖子，教师和管理员无此限制
    if (current_user.role.name == "学生"):
        pagination = Post.query.filter(and_(Post.pro_id==pro_id, Post.display_time < now)).order_by(Post.star.desc(), Post.create_time.desc()).paginate(page, per_page=current_app.config['PER_PAGE']) 
    else:
        pagination = Post.query.filter(Post.pro_id==pro_id).order_by(Post.star.desc(), Post.create_time.desc()).paginate(page, per_page=current_app.config['PER_PAGE']) 
    latest = pagination.items
    problem = Problem.query.filter_by(id=pro_id).first()
    return render_template('index.html', template_folder='templates', latest=latest, pagination=pagination, tag=tag, problems=problems, pro_id=pro_id, name=problem.name,mod="lastcreate")


@index_bp.route('/index/mostlike/<pro_id>')
@login_required
# 按点赞数降序排列显示帖子
def indexpro_mostlike(pro_id):
    tag = (Post.query.filter_by(pro_id=pro_id).count() > current_app.config['PER_PAGE'])    # 若查询结果多于每页最多显示条数，则需要进行分页显示
    problems = Problem.query.all()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    page = request.args.get('page', 1, type=int)
    # 学生只能查看超过ddl的问题的标准回答帖子，教师和管理员无此限制
    if (current_user.role.name == "学生"):
        pagination = Post.query.filter(and_(Post.pro_id==pro_id, Post.display_time < now)).order_by(Post.star.desc(), Post.like.desc()).paginate(page, per_page=current_app.config['PER_PAGE']) 
    else:
        pagination = Post.query.filter(Post.pro_id==pro_id).order_by(Post.star.desc(), Post.like.desc()).paginate(page, per_page=current_app.config['PER_PAGE']) 
    latest = pagination.items
    problem = Problem.query.filter_by(id=pro_id).first()
    return render_template('index.html', template_folder='templates', latest=latest, pagination=pagination, tag=tag, problems=problems, pro_id=pro_id,name=problem.name, mod="mostlike")


@index_bp.route('/index/delete/<pro_id>', methods=['POST', 'GET'])
def deletePro(pro_id):
    r = Problem.query.filter_by(id=pro_id).first()
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for('.index'))


@index_bp.route('/index/my/<pro_id>')
@login_required
# 显示本人创作的所有帖子
def indexpro_my(pro_id):
    tag = (Post.query.filter_by(pro_id=pro_id).count() > current_app.config['PER_PAGE'])    # 若查询结果多于每页最多显示条数，则需要进行分页显示
    problems = Problem.query.all()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    page = request.args.get('page', 1, type=int)
    # 由于是本人创作，因此不存在隐藏ddl前问题的标准回答的帖子的情况
    pagination = Post.query.filter(and_(Post.pro_id==pro_id, Post.author_id==current_user.id)).paginate(page, per_page=current_app.config['PER_PAGE'])
    latest = pagination.items
    problem = Problem.query.filter_by(id=pro_id).first()
    return render_template('index.html', template_folder='templates', latest=latest, pagination=pagination, tag=tag, problems=problems, pro_id=pro_id, name=problem.name,mod="my")


@index_bp.route('/index/fork/<pro_id>')
@login_required
# 显示本人收藏的所有帖子
def indexpro_fork(pro_id):
    tag = (Post.query.filter_by(pro_id=pro_id).count() > current_app.config['PER_PAGE'])    # 若查询结果多于每页最多显示条数，则需要进行分页显示
    problems = Problem.query.all()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    page = request.args.get('page', 1, type=int)
    # 由于是已经收藏过的，因此不存在隐藏ddl前问题的标准回答的帖子的情况
    pagination = Post.query.outerjoin(ForkLog).filter(and_(Post.pro_id==pro_id, and_(Post.id==ForkLog.post_id, current_user.id==ForkLog.user_id))).paginate(page, per_page=current_app.config['PER_PAGE'])
    latest = pagination.items
    problem = Problem.query.filter_by(id=pro_id).first()
    return render_template('index.html', template_folder='templates', latest=latest, pagination=pagination, tag=tag, problems=problems, pro_id=pro_id, name=problem.name, mod="fork")
