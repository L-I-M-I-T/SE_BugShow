from werkzeug.security import generate_password_hash, check_password_hash
from flask_avatars import Identicon
from extensions import db
from flask_login import UserMixin, current_user
from settings import *
import datetime

# 实体表

class User(db.Model, UserMixin):
    __tablename__ = 't_user'
    # 基本属性
    id = db.Column(db.INTEGER, primary_key=True, nullable=False, index=True, autoincrement=True)        # 用户id
    username = db.Column(db.String(40), nullable=False, index=True, unique=True, comment='user name')   # 用户账号名称
    nickname = db.Column(db.String(40), nullable=False, unique=True, comment='user nick name')          # 用户显示昵称
    password = db.Column(db.String(256), comment='user password')                                       # 用户登录密码
    email = db.Column(db.String(128), unique=True, nullable=False, comment='user register email')       # 用户注册邮箱
    avatar = db.Column(db.String(1024), nullable=False, comment='user avatar')                          # 用户头像对应图片的存储路径
    unreadnotice = db.Column(db.INTEGER, nullable=False, default=0)                                     # 用户未读通知条数    
    starpost = db.Column(db.INTEGER, nullable=False, default=0)                                         # 用户收藏的帖子数量

    # 外键
    role_id = db.Column(db.INTEGER, db.ForeignKey('t_role.id'), default=3, comment='user role id default is 3, that is student role')   #用户对应的角色的id

    # 关联实体
    role = db.relationship('Role', back_populates='user')

    #方法
    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def generate_avatar(self):  # 为新注册用户根据登录IP地址生成初始哈希头像
         icon = Identicon()
         files = icon.generate(self.username)
         self.avatar = "resources/avatars/" + files[2]
    
    def set_avatar(self, avatar):
        self.avatar = avatar

class Role(db.Model):
    __tablename__ = 't_role'

    # 基本属性
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)    # 角色id
    name = db.Column(db.String(40), nullable=False)                                 # 角色名称

    # 关联实体
    user = db.relationship('User', back_populates='role', cascade='all')

class Problem(db.Model):
    __tablename__ = 't_problem'

    # 基本属性
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)    # 问题id
    name = db.Column(db.String(40), nullable=False)                     # 问题标题

    # 关联实体
    posts = db.relationship('Post', cascade='all')


class Post(db.Model):
    __tablename__ = 't_post'

    # 基本属性
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)    # 帖子id
    title = db.Column(db.String(100), index=True, nullable=False)                   # 帖子标题
    content = db.Column(db.TEXT, nullable=False)                                    # 帖子内容（富文本形式）
    textplain = db.Column(db.TEXT, nullable=False)                                  # 帖子内容（纯文本形式）

    # 外键
    pro_id = db.Column(db.INTEGER, db.ForeignKey('t_problem.id'))                   # 帖子对应的问题id
    author_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))                   # 帖子的作者对应的用户id
    like = db.Column(db.INTEGER, default=0, comment='likes from people')            # 帖子被点赞的数量
    fork = db.Column(db.INTEGER, default=0, comment='forks from people')            # 帖子被收藏的数量
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)             # 帖子创建的时间
    update_time = db.Column(db.DateTime, default=datetime.datetime.now)             # 帖子最后更新的时间
    display_time = db.Column(db.DateTime, default=datetime.datetime.now)            # 帖子开始显示的时间（用于在ddl前隐藏标准答案）
    
    # 关联实体
    comments = db.relationship('Comments', cascade='all')
    likelog = db.relationship('LikeLog', cascade='all')
    forklog = db.relationship("ForkLog", cascade='all')
    pro = db.relationship('Problem')
    user = db.relationship('User')

    # 方法
    def can_delete(self):
        # 学生只能删除自己发布的帖子，教师和管理员能够删除所有的帖子
        return (current_user.id == self.author_id or  current_user.role.name == '管理员' or current_user.role.name == '老师')


class Comments(db.Model):
    __tablename__ = 't_comments'

    # 基本属性
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)            # 评论id
    body = db.Column(db.Text)                                                   # 评论内容（纯文本）

    # 外键
    replied_id = db.Column(db.INTEGER, db.ForeignKey('t_comments.id'))          # 该评论回复的评论id
    author_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))               # 评论的作者对应的用户id
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))                 # 该评论所属的问题的id

    # 关联实体
    post = db.relationship('Post')
    author = db.relationship('User')
    replies = db.relationship('Comments', cascade='all')
    replied = db.relationship('Comments', remote_side=[id])

    # 方法
    def can_delete(self):
        # 学生只能删除自己发布的评论，教师和管理员能够删除所有的评论
        return (current_user.id == self.author_id or  current_user.role.name == '管理员' or current_user.role.name == '老师')


class VerifyCode(db.Model):
    __tablename__ = 't_ver_code'

    # 基本属性
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)                    # 验证码id 
    value = db.Column(db.INTEGER, nullable=False)                                       # 验证码数值 
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)                  # 验证码生成的时间 
    expire_time = db.Column(db.DateTime, nullable=False)                                # 验证码有效时间 
    is_work = db.Column(db.Boolean, default=True)                                       # 验证码是否有效 
    who = db.Column(db.String(40), nullable=False, comment='this ver code belong who')  # 验证码的接收者

class Notice(db.Model):
    __tablename__ = 't_notice'

    # 基本属性
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)            # 通知id
    title = db.Column(db.String(100), index=True, nullable=False)                           # 通知标题
    content = db.Column(db.TEXT, nullable=False)                                            # 通知内容（纯文本）

    # 外键
    author_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))                           # 通知的作者对应的用户id

    # 关联实体
    author = db.relationship('User')
    noticestatus = db.relationship('NoticeStatus', cascade='all')

# 关系表

class NoticeStatus(db.Model):
    __tablename__ = 't_noticestatus'

    user_id = db.Column(db.INTEGER,db.ForeignKey('t_user.id'),primary_key=True)                    # 收件箱用户id
    notice_id = db.Column(db.INTEGER,db.ForeignKey('t_notice.id'),primary_key=True)                # 收件箱中通知的id
    status = db.Column(db.Enum('read','unread','delete'),nullable=False,server_default='unread')   # 收件箱中通知的状态（已读，未读，已删除）

    user = db.relationship('User')

class LikeLog(db.Model):
    __tablename__ = 't_likestate'

    user_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'),primary_key=True)    # 点赞的用户id
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'),primary_key=True)    # 被点赞的帖子id

class ForkLog(db.Model):
    __tablename__ = 't_startstate'

    user_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'),primary_key=True)    # 收藏的用户id
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'),primary_key=True)    # 被点赞的帖子id
