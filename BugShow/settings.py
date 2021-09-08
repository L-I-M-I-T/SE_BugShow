import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_HEIGHT = 400
    CKEDITOR_FILE_UPLOADER = 'normal.image_upload'
    DATABASE_NAME = "se"
    DATABASE_CHARSET = "utf8mb4"
    DATABASE_USER = "root"
    DATABASE_PWD  = "wangtian"
    DATABASE_HOST = "127.0.0.1"
    DATABASE_PORT = "3306"
    BUGSHOW_MAIL_SUBJECT_PRE = 'BugShow'
    MAIL_SERVER= "smtp.qq.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "1193354569@qq.com"
    MAIL_PASSWORD = "hezadrhymfjhjcig"
    MAIL_DEFAULT_SENDER = ('BugShow Administrator', MAIL_USERNAME)
    POST_PER_PAGE = 7                                                       # 每页显示的最大帖子数量
    UPLOAD_PATH = os.path.join(basedir, 'bugshow/static/resources')
    AVATARS_PATH = UPLOAD_PATH + '/avatars/'
    FILE_PATH = UPLOAD_PATH + '/file/'
    AVATARS_IDENTICON_ROWS = 15
    AVATARS_IDENTICON_COLS = 15
    AVATARS_IDENTICON_BG = "#000000"
    AVATARS_SIZE_TUPLE = (50, 50, 50)
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}?charset={}'.format(DATABASE_USER, DATABASE_PWD, DATABASE_HOST, DATABASE_NAME, DATABASE_CHARSET)
    VERCODE_VALID_TIME = 10
    SECRET_KEY = os.urandom(32)
