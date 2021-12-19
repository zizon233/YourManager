from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo


class RegisterationForm(FlaskForm):
    user_id = StringField("user_id", validators=[DataRequired()])
    user_name = StringField("user_name", validators=[DataRequired()])
    password = PasswordField(
        "password", validators=[DataRequired(), EqualTo("re_password")]
    )
    re_password = PasswordField("re_password", validators=[DataRequired()])


class LoginForm(FlaskForm):
    user_id = StringField("user_id", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
