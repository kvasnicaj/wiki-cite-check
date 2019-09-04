from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PageForm(FlaskForm):
    page = StringField('Page', validators=[DataRequired()])
    submit = SubmitField('Hledat')
