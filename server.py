from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import background  

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba2451'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['CELERY_BROKER_URL']='redis://localhost:6379',
app.config['CELERY_RESULT_BACKEND']='redis://localhost:6379'

celery = background.make_celery(app)

import routes
