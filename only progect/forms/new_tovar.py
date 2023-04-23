from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    content = TextAreaField("О товаре")
    cena = StringField('Цена, ₽')
    submit = SubmitField('Добавить')