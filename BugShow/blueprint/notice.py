import datetime
from operator import methodcaller
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from models import *
from forms import CreateNoticeForm, EditPostForm
from flask_login import login_required, current_user
from extensions import db
from sqlalchemy import and_
from utils import get_text_plain
from sqlalchemy.sql.expression import func

notice_bp = Blueprint('notice', __name__, url_prefix='/notice')

@notice_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_notice():
    form = CreateNoticeForm()
    if form.validate_on_submit():
        # 根据表单参数创建新的通知数据
        title = form.title.data
        content = form.body.data
        notice = Notice(title=title, content=content, author_id=current_user.id)
        db.session.add(notice)
        db.session.commit()

        # 插入每个学生对这条消息的未读记录
        role_id = Role.query.filter(Role.name == "学生").first().id
        students = User.query.filter(User.role_id == role_id).all()
        for stu in students:
            ns = NoticeStatus(user_id = stu.id,notice_id=notice.id,status='unread')
            stu.unreadnotice = stu.unreadnotice + 1
            db.session.add(ns)
        db.session.commit()
        flash('通知发布成功!','success')
        return redirect(url_for('index_bp.index'))
    return render_template('new-notice.html', template_folder='templates', form=form)

@notice_bp.route('/browse',methods=['GET','POST'])
@login_required
def browse_notice():
    # 以页式结构显示所有通知
    page = request.args.get('page', 1, type=int)
    pagination = Notice.query.paginate(page, per_page=current_app.config['PER_PAGE'])    
    latest = pagination.items
    return render_template('browse-notice.html', template_folder='templates', latest=latest,pagination=pagination)

@notice_bp.route('/confirm/<notice_id>', methods=['GET'])
@login_required
def confirm(notice_id):
    current_user.unreadnotice = current_user.unreadnotice - 1
    ns = NoticeStatus.query.filter_by(user_id = current_user.id,notice_id=notice_id).first()
    ns.status = 'read'
    db.session.commit()
    return redirect(url_for('notice.browse_notice'))

@notice_bp.route('/read/<notice_id>', methods=['GET'])
def read(notice_id):
    page = request.args.get('page', default=1, type=int)
    notice = Notice.query.get_or_404(notice_id)
    per_page = current_app.config['PER_PAGE']
    return render_template('read-notice.html', template_folder='templates', notice=notice, c_tag=True, emoji_urls="#", per_page=per_page, page=page)

@notice_bp.route('/delete/<notice_id>', methods=['GET'])
@login_required
def delete(notice_id):  # 发布者对通知进行删除
    notice = Notice.query.get_or_404(notice_id)
    res = NoticeStatus.query.filter_by(notice_id=notice_id).all()
    if res:
        for re in res:
            if (re.status == 'unread'):
                re.user.unreadnotice = re.user.unreadnotice - 1
    db.session.delete(notice)
    db.session.commit()
    flash('通知删除成功!', 'success')
    return redirect(url_for('notice.browse_notice'))

@notice_bp.route('/sdelete/<notice_id>', methods=['GET'])
@login_required
def sdelete(notice_id): # 接收者对通知进行删除 
    notice = NoticeStatus.query.filter(and_(NoticeStatus.notice_id == notice_id, NoticeStatus.user_id == current_user.id)).first()
    notice.status = "delete"
    db.session.commit()
    flash('通知删除成功!', 'success')
    return redirect(url_for('notice.browse_notice'))
