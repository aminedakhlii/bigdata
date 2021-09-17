from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
import elasticfuncs as ef


class SearchForm(FlaskForm):
    index = SelectField('index')
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.index.choices = ef.getIndices() + ['all']