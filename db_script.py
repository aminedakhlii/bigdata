from server import db
from models import Fields, FieldsMap
import elasticfuncs as ef

f = Fields.query.all()
for field in f: 
    map = FieldsMap(old=field.name,new=field.name)
    db.session.add(map)
    db.session.commit()