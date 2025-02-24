from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/add_expense', methods=['POST'])
def add_expense():
    month = request.form['month'].capitalize()
    product_name = request.form['product_name']
    try:
        amount = float(request.form['amount'])
    except ValueError:
        flash('Please enter a valid number for the amount.')
        return redirect(url_for('index'))
    
    if month not in ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']:
        flash('Invalid month name. Please enter a correct month name.')
        return redirect(url_for('index'))
    
    new_expense = Expense(month=month, product_name=product_name, amount=amount)
    db.session.add(new_expense)
    db.session.commit()
    flash('Expense added successfully!')
    return redirect(url_for('index'))



@app.route('/view_expenses/<month>')
def view_month_expenses(month):
    expenses = Expense.query.filter_by(month=month).all()
    total_expense = sum(exp.amount for exp in expenses)
    return render_template('month_expenses.html', month=month, expenses=expenses, total_expense=total_expense)



@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    errors = {}  # Initialize errors as an empty dictionary
    
    if request.method == 'POST':
        month = request.form['month'].capitalize()
        product_name = request.form['product_name']
        amount = request.form['amount']

        # Validate month
        valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                        'July', 'August', 'September', 'October', 'November', 'December']
        if month not in valid_months:
            errors['month'] = "Invalid month name. Please enter a correct month name."

        # Validate amount
        try:
            amount = float(amount)
        except ValueError:
            errors['amount'] = "Please enter a valid number for amount."

        if errors:
            return render_template('edit_expense.html', expense=expense, errors=errors)

        # Update the expense
        expense.month = month
        expense.product_name = product_name
        expense.amount = amount
        db.session.commit()
        flash('Expense updated successfully!')
        return redirect(url_for('view_month_expenses', month=expense.month))

    return render_template('edit_expense.html', expense=expense, errors=errors)



@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense successfully deleted!')
    return redirect(url_for('view_month_expenses', month=expense.month))

if __name__ == '__main__':
    app.run(debug=True)
