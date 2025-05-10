from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, TransactionForm, CategoryForm
from extensions import db, login_manager
from datetime import datetime, date
import pandas as pd
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)

# Define user_loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import models after extensions are initialized
from models import User, Transaction, Category, Tag

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # Add default categories
        default_categories = [
            Category(name="Salary", type="income", user_id=user.id),
            Category(name="Other Income", type="income", user_id=user.id),
            Category(name="Rent", type="expense", user_id=user.id),
            Category(name="Groceries", type="expense", user_id=user.id),
            Category(name="Utilities", type="expense", user_id=user.id)
        ]
        db.session.add_all(default_categories)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Handle filtering
    category_id = request.args.get('category_id', type=int)
    tag_id = request.args.get('tag_id', type=int)
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if tag_id:
        query = query.join(transaction_tags).filter(transaction_tags.c.tag_id == tag_id)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Calculate summary metrics
    income = sum(t.amount for t in transactions if t.category.type == 'income')
    expense = sum(t.amount for t in transactions if t.category.type == 'expense')
    savings = income - expense

    # Prepare data for Chart.js
    chart_data = {'dates': [], 'income': [], 'expense': []}
    if transactions:
        transaction_data = [
            {'date': t.date.strftime('%Y-%m-%d'), 'amount': t.amount, 'category': t.category.type}
            for t in transactions
        ]
        df = pd.DataFrame(transaction_data)
        
        if not df.empty:
            try:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                income_df = df[df['category'] == 'income'].resample('D').sum().reindex(df.index, fill_value=0)
                expense_df = df[df['category'] == 'expense'].resample('D').sum().reindex(df.index, fill_value=0)
                dates = [d.strftime('%Y-%m-%d') for d in df.index]
                income_data = income_df['amount'].tolist()
                expense_data = expense_df['amount'].tolist()
                chart_data = {
                    'dates': dates,
                    'income': income_data,
                    'expense': expense_data
                }
            except Exception as e:
                logger.error(f"Error processing chart data: {e}")
                flash('Error generating chart data.', 'danger')
    
    logger.debug(f"Chart data: {chart_data}")

    # Get top 5 incomes and expenses for the current month
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    end_of_month = date(today.year, today.month + 1, 1) if today.month < 12 else date(today.year + 1, 1, 1)
    
    top_incomes = Transaction.query.join(Category).filter(
        Transaction.user_id == current_user.id,
        Category.type == 'income',
        Transaction.date.between(start_of_month, end_of_month)
    ).order_by(Transaction.amount.desc()).limit(5).all()
    
    top_expenses = Transaction.query.join(Category).filter(
        Transaction.user_id == current_user.id,
        Category.type == 'expense',
        Transaction.date.between(start_of_month, end_of_month)
    ).order_by(Transaction.amount.desc()).limit(5).all()

    # Get all categories and tags for filtering
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    tags = Tag.query.filter_by(user_id=current_user.id).order_by(Tag.name).all()

    return render_template('dashboard.html', user=current_user,
                           transactions=transactions,
                           income=income, expense=expense, savings=savings,
                           chart_data=json.dumps(chart_data, default=str),
                           top_incomes=top_incomes,
                           top_expenses=top_expenses,
                           current_month=today.strftime('%B %Y'),
                           categories=categories,
                           tags=tags,
                           selected_category_id=category_id,
                           selected_tag_id=tag_id)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        txn = Transaction(
            date=form.date.data or datetime.today(),
            amount=form.amount.data,
            category_id=form.category.data,
            description=form.description.data,
            user_id=current_user.id
        )
        # Assign selected tags
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        txn.tags = selected_tags
        db.session.add(txn)
        db.session.commit()
        flash('Transaction added successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_transaction.html', form=form)

@app.route('/edit/<int:txn_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(txn_id):
    txn = Transaction.query.get_or_404(txn_id)
    if txn.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = TransactionForm()
    if form.validate_on_submit():
        txn.date = form.date.data or datetime.today()
        txn.amount = form.amount.data
        txn.category_id = form.category.data
        txn.description = form.description.data
        txn.tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        db.session.commit()
        flash('Transaction updated successfully.', 'success')
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        form.date.data = txn.date
        form.amount.data = txn.amount
        form.category.data = txn.category_id
        form.description.data = txn.description
        form.tags.data = [tag.id for tag in txn.tags]
    
    return render_template('edit_transaction.html', form=form, txn=txn)

@app.route('/delete/<int:txn_id>')
@login_required
def delete_transaction(txn_id):
    txn = Transaction.query.get_or_404(txn_id)
    if txn.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    db.session.delete(txn)
    db.session.commit()
    flash('Transaction deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            type=form.type.data,
            user_id=current_user.id
        )
        try:
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully.', 'success')
        except:
            db.session.rollback()
            flash('Category name already exists.', 'danger')
        return redirect(url_for('manage_categories'))
    
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    return render_template('categories.html', form=form, categories=categories)

@app.route('/categories/delete/<int:category_id>')
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('manage_categories'))
    if category.transactions:
        flash('Cannot delete category with associated transactions.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully.', 'success')
    return redirect(url_for('manage_categories'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)