from server import db, app

class Fields(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class FieldsMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    old = db.Column(db.String(100), nullable=False)
    new = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Integer,nullable=False)

class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)  
    isKey = db.Column(db.Integer,nullable=False)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.String(100), nullable=False)  
    number = db.Column(db.Integer,nullable=False) 
    lines = db.Column(db.Integer)