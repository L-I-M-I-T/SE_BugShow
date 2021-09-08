import datetime
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from models import *
from forms import CreatePostForm, EditPostForm, CreateAnswerForm, EditAnswerForm
from flask_login import login_required, current_user
from extensions import db
from utils import get_text_plain

post_bp = Blueprint('post', __name__, url_prefix='/post')

@post_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        # 获取表单中的参数
        title = form.title.data
        problem = form.problem.data
        content = form.body.data
        textplain = get_text_plain(content)

        post = Post(title=title, pro_id=problem, content=content, author_id=current_user.id, textplain=textplain)
        db.session.add(post)
        db.session.commit()
        flash('帖子发布成功!', 'success')
        return redirect(url_for('index_bp.index'))
    return render_template('new-post.html', template_folder='templates', form=form)


@post_bp.route('/newt', methods=['GET', 'POST'])
@login_required
def newt_post():
    form = CreateAnswerForm()
    if form.validate_on_submit():
        # 获取表单中的参数
        title = form.title.data
        problem = form.problem.data
        content = form.body.data
        textplain = get_text_plain(content)
        dt = form.dt.data
        
        post = Post(title=title, pro_id=problem, content=content, author_id=current_user.id, textplain=textplain, display_time = dt)
        db.session.add(post)
        db.session.commit()
        flash('解答发布成功!', 'success')
        return redirect(url_for('index_bp.index'))
    return render_template('newt-post.html', template_folder='templates', form=form)


@post_bp.route('/read/<post_id>', methods=['GET'])
@login_required
def read(post_id):
    page = request.args.get('page', default=1, type=int)
    post = Post.query.get_or_404(post_id)
    per_page = current_app.config['PER_PAGE']
    pagination = Comments.query.filter(Comments.post_id == post_id).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('read-post.html', post=post, c_tag=True, comments=comments, pagination=pagination, emoji_urls="#", per_page=per_page, page=page)


@post_bp.route('/edit/<post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    form = EditPostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        # 获取表单中的参数
        title = form.title.data
        pro = form.problem.data
        content = form.body.data
        post.title = title
        post.pro_id = pro
        post.content = content
        post.update_time = datetime.datetime.now()

        ep = Post.query.filter_by(title=title).first()
        # 修改标题不能是其他已经存在帖子的标题
        if ep and ep.id != post.id:
            flash('该帖子标题已经存在', 'danger')
            return redirect(url_for('.edit', post_id=post_id))
        db.session.commit()
        flash('帖子编辑成功!', 'success')
        return redirect(url_for('.read', post_id=post_id))
    form.title.data = post.title
    form.body.data = post.content
    form.problem.data = post.pro
    return render_template('edit-post.html', post=post, form=form)


@post_bp.route('/editt/<post_id>', methods=['GET', 'POST'])
@login_required
def editt(post_id):
    form = EditAnswerForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        # 获取表单中的参数
        title = form.title.data
        pro = form.problem.data
        content = form.body.data
        dt = form.dt.data

        ep = Post.query.filter_by(title=title).first()
        # 修改标题不能是其他已经存在帖子的标题
        if ep and ep.id != post.id:
            flash('该帖子标题已经存在', 'danger')
            return redirect(url_for('.editt', post_id=post_id))
        post.title = title
        post.pro_id = pro
        post.content = content
        post.display_time = dt
        post.update_time = datetime.datetime.now()
        db.session.commit()
        flash('帖子编辑成功!', 'success')
        return redirect(url_for('.read', post_id=post_id))
    form.title.data = post.title
    form.body.data = post.content
    form.problem.data = post.pro
    form.dt.data = post.display_time
    return render_template('editt-post.html', post=post, form=form)


@post_bp.route('/delete/<post_id>', methods=['GET'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_delete():
        db.session.delete(post)
        db.session.commit()
        flash('帖子删除成功!', 'success')
    else:
        flash('没有删除权限!', 'danger')
    return redirect(url_for('index_bp.index'))


@post_bp.route('/post-comment', methods=['POST'])
@login_required
def post_comment():
    # 获取表单中的参数
    comment_content = request.form.get('commentContent')
    post_id = request.form.get('postId')

    post = Post.query.get_or_404(post_id)
    com = Comments(body=comment_content, post_id=post_id, author_id=current_user.id)
    post.update_time = datetime.datetime.now()
    db.session.add(com)
    db.session.commit()
    return jsonify({'tag': 1})


@post_bp.route('/reply-comment', methods=['POST'])
@login_required
def reply_comment():
    comment_id = request.form.get('comment_id')
    # 用于处理消息通知
    comment = request.form.get('comment')
    post_id = request.form.get('post_id')
    post = Post.query.get_or_404(post_id)
    reply = Comments(body=comment, replied_id=comment_id, author_id=current_user.id, post_id=post_id)
    post.update_time = datetime.datetime.now()

    db.session.add(reply)
    db.session.commit()
    return jsonify({'tag': 1})


@post_bp.route('/star/<post_id>', methods=['GET'])
@login_required
def star(post_id):
    post = Post.query.get_or_404(post_id)
    if post.star == 0 :
        post.star = 1
        db.session.commit()
        flash('标星解答成功!','success')
    else :
        post.star = 0
        db.session.commit()
        flash('取消标星成功!','success')
    return redirect(url_for('.read', post_id=post_id))


@post_bp.route('/like/<post_id>', methods=['GET', 'POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    log = LikeLog.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if log :
        post.like -= 1
        db.session.delete(log)
        db.session.commit()
        flash('取消点赞成功','success')
    else :
        post.like += 1
        db.session.add(LikeLog(user_id=current_user.id, post_id=post_id))
        db.session.commit()
        flash('点赞成功','success')
    return redirect(url_for('.read', post_id=post_id))


@post_bp.route('/fork/<post_id>', methods=['GET', 'POST'])
@login_required
def fork(post_id):
    post = Post.query.get_or_404(post_id)
    log = ForkLog.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if log :
        post.fork -= 1
        db.session.delete(log)
        db.session.commit()
        flash('取消收藏成功','success')
    else :
        post.fork += 1
        db.session.add(ForkLog(user_id=current_user.id, post_id=post_id))
        db.session.commit()
        flash('收藏成功','success')
    return redirect(url_for('.read', post_id=post_id))


@post_bp.route('/delete-comment/<comment_id>', methods=['GET'])
@login_required
def delete_comment(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    if comment.can_delete():
        db.session.delete(comment)
        db.session.commit()
        flash('评论删除成功!', 'success')
    else:
        flash('没有删除权限!', 'danger')
    return redirect(url_for('index_bp.index'))
