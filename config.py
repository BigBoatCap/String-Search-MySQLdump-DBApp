from flask import Flask

app = Flask(__name__)

DEBUG = False
UPLOAD_FOLDER = 'C:/Users/alexandr.dragutan/PycharmProjects/String-Search-MySQLdump-DBApp/upload/'
DBHOST = 'localhost'
DBUSER = 'root'
DBPASSWORD = 'root_p@$$VVD'
ALLOWED_EXTENSIONS = 'sql'
SECRET_KEY = 'blahblahblaj'