class Config:
    SECRET_KEY = 'nahtzm1z3n'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:caitoicaom8@localhost/language_center'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'thantam2309@gmail.com'
    MAIL_PASSWORD = 'iwok ydje ekmo jfkq'
    MAIL_DEFAULT_SENDER = ("Language Center", MAIL_USERNAME)

config = Config()