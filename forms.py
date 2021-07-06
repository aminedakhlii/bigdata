from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
import elasticfuncs as ef


class SearchForm(FlaskForm):
    phone_FB = StringField('phone_FB')
    facebook_UID = StringField('facebook_UID')
    first_name_FB = StringField('first_name_FB')
    last_name_FB = StringField('last_name_FB')
    gender_FB = StringField('gender_FB')
    city_FB = StringField('city_FB')
    country_FB = StringField('country_FB')
    city_birth_FB = StringField('city_birth_FB')
    country_birth_FB = StringField('country_birth_FB')
    status_FB = StringField('status_FB')
    company_FB = StringField('company_FB')
    last_publication_FB = StringField('last_publication_FB')
    other_FB1 = StringField('other_FB1')
    other_FB2 = StringField('other_FB2')
    mail_FB = StringField('mail_FB')
    hbd_FB = StringField('hbd_FB')
    index = SelectField('index', choices=ef.getIndices() + ['all'])
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.index.choices = ef.getIndices()
