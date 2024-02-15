from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class FormTool(FlaskForm):
    symbol = StringField('Symbol')
    submit = SubmitField('Submit')
