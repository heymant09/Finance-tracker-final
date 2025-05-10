from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange
from flask_login import current_user
from models import Category, Tag

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=256)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class TransactionForm(FlaskForm):
    date = DateField("Date", format='%Y-%m-%d', render_kw={"type": "date"})
    amount = FloatField("Amount", validators=[DataRequired(), NumberRange(min=0.01, message="Amount must be positive")])
    category = SelectField("Category", validators=[DataRequired()], coerce=int)
    description = TextAreaField("Description")
    tags = SelectMultipleField("Tags", coerce=int)
    submit = SubmitField("Add Transaction")

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        if current_user.is_authenticated:
            self.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()]
            self.tags.choices = [(t.id, t.name) for t in Tag.query.filter_by(user_id=current_user.id).order_by(Tag.name).all()]
        else:
            self.category.choices = []
            self.tags.choices = []

class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(min=1, max=50)])
    type = SelectField("Type", choices=[('income', 'Income'), ('expense', 'Expense')], validators=[DataRequired()])
    submit = SubmitField("Save Category")