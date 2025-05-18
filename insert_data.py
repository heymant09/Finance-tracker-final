from app import app, db
from models import User, Category, Tag, Transaction
from werkzeug.security import generate_password_hash
from datetime import datetime, date

def insert_data():
    with app.app_context():
        # Create User: Hemant
        user = User.query.filter_by(username="Hemant").first()
        if not user:
            user = User(
                username="Hemant",
                password=generate_password_hash("123456")
            )
            db.session.add(user)
            db.session.commit()
            print("Created user: Hemant")
        else:
            print("User Hemant already exists")

        # Create Categories
        categories = [
            {"name": "Salary", "type": "income"},
            {"name": "Side Hustle", "type": "income"},
            {"name": "Dividends", "type": "income"},
            {"name": "Refunds", "type": "income"},
            {"name": "Mortgage", "type": "expense"},
            {"name": "Supermarket", "type": "expense"},
            {"name": "Bills", "type": "expense"},
            {"name": "Commute", "type": "expense"},
            {"name": "Restaurants", "type": "expense"},
            {"name": "Leisure", "type": "expense"},
            {"name": "Electronics", "type": "expense"},
            {"name": "Medical", "type": "expense"},
        ]

        for cat in categories:
            if not Category.query.filter_by(name=cat["name"], user_id=user.id).first():
                category = Category(name=cat["name"], type=cat["type"], user_id=user.id)
                db.session.add(category)
                print(f"Added category: {cat['name']}")

        db.session.commit()

        # Create Tags
        tags = ["Job", "Home", "Monthly", "Priority", "Vacation", "Fun", "Investments"]
        for tag_name in tags:
            if not Tag.query.filter_by(name=tag_name, user_id=user.id).first():
                tag = Tag(name=tag_name, user_id=user.id)
                db.session.add(tag)
                print(f"Added tag: {tag_name}")

        db.session.commit()

        # Fetch category and tag objects for transactions
        category_dict = {cat.name: cat for cat in Category.query.filter_by(user_id=user.id).all()}
        tag_dict = {tag.name: tag for tag in Tag.query.filter_by(user_id=user.id).all()}

        # Create Transactions
        transactions = [
            # February 2025
            {"date": date(2025, 2, 5), "amount": 5500.00, "category": "Salary", "description": "Monthly salary", "tags": ["Job", "Monthly"]},
            {"date": date(2025, 2, 5), "amount": 1500.00, "category": "Mortgage", "description": "Home mortgage payment", "tags": ["Home", "Monthly"]},
            {"date": date(2025, 2, 6), "amount": 180.00, "category": "Supermarket", "description": "Weekly supermarket shopping", "tags": ["Home"]},
            {"date": date(2025, 2, 8), "amount": 100.00, "category": "Bills", "description": "Electricity bill", "tags": ["Monthly"]},
            {"date": date(2025, 2, 10), "amount": 60.00, "category": "Restaurants", "description": "Dinner at Italian restaurant", "tags": ["Fun"]},
            {"date": date(2025, 2, 12), "amount": 250.00, "category": "Side Hustle", "description": "Graphic design gig", "tags": ["Job"]},
            {"date": date(2025, 2, 15), "amount": 400.00, "category": "Electronics", "description": "New headphones", "tags": ["Home"]},
            {"date": date(2025, 2, 18), "amount": 120.00, "category": "Commute", "description": "Monthly bus pass", "tags": ["Monthly"]},
            {"date": date(2025, 2, 22), "amount": 90.00, "category": "Leisure", "description": "Amusement park tickets", "tags": ["Fun"]},

            # March 2025
            {"date": date(2025, 3, 5), "amount": 5500.00, "category": "Salary", "description": "Monthly salary", "tags": ["Job", "Monthly"]},
            {"date": date(2025, 3, 5), "amount": 1500.00, "category": "Mortgage", "description": "Home mortgage payment", "tags": ["Home", "Monthly"]},
            {"date": date(2025, 3, 7), "amount": 190.00, "category": "Supermarket", "description": "Weekly supermarket shopping", "tags": ["Home"]},
            {"date": date(2025, 3, 8), "amount": 110.00, "category": "Bills", "description": "Water bill", "tags": ["Monthly"]},
            {"date": date(2025, 3, 10), "amount": 300.00, "category": "Medical", "description": "Dental checkup", "tags": ["Priority"]},
            {"date": date(2025, 3, 15), "amount": 200.00, "category": "Dividends", "description": "Stock dividends", "tags": ["Investments"]},
            {"date": date(2025, 3, 18), "amount": 70.00, "category": "Restaurants", "description": "Lunch with colleagues", "tags": ["Fun"]},
            {"date": date(2025, 3, 20), "amount": 600.00, "category": "Electronics", "description": "New monitor", "tags": ["Home"]},
            {"date": date(2025, 3, 25), "amount": 150.00, "category": "Commute", "description": "Flight for conference", "tags": ["Vacation"]},

            # April 2025
            {"date": date(2025, 4, 5), "amount": 5500.00, "category": "Salary", "description": "Monthly salary", "tags": ["Job", "Monthly"]},
            {"date": date(2025, 4, 5), "amount": 1500.00, "category": "Mortgage", "description": "Home mortgage payment", "tags": ["Home", "Monthly"]},
            {"date": date(2025, 4, 6), "amount": 170.00, "category": "Supermarket", "description": "Weekly supermarket shopping", "tags": ["Home"]},
            {"date": date(2025, 4, 8), "amount": 95.00, "category": "Bills", "description": "Internet bill", "tags": ["Monthly"]},
            {"date": date(2025, 4, 12), "amount": 150.00, "category": "Refunds", "description": "Online purchase refund", "tags": ["Home"]},
            {"date": date(2025, 4, 15), "amount": 80.00, "category": "Leisure", "description": "Streaming subscriptions", "tags": ["Fun"]},
            {"date": date(2025, 4, 20), "amount": 60.00, "category": "Commute", "description": "Uber rides", "tags": ["Vacation"]},
            {"date": date(2025, 4, 25), "amount": 250.00, "category": "Restaurants", "description": "Anniversary dinner", "tags": ["Fun"]},

            # May 2025 (partial month, up to May 12)
            {"date": date(2025, 5, 5), "amount": 5500.00, "category": "Salary", "description": "Monthly salary", "tags": ["Job", "Monthly"]},
            {"date": date(2025, 5, 5), "amount": 1500.00, "category": "Mortgage", "description": "Home mortgage payment", "tags": ["Home", "Monthly"]},
            {"date": date(2025, 5, 6), "amount": 185.00, "category": "Supermarket", "description": "Weekly supermarket shopping", "tags": ["Home"]},
            {"date": date(2025, 5, 8), "amount": 105.00, "category": "Bills", "description": "Gas bill", "tags": ["Monthly"]},
            {"date": date(2025, 5, 10), "amount": 350.00, "category": "Side Hustle", "description": "Consulting fee", "tags": ["Job"]},
            {"date": date(2025, 5, 12), "amount": 90.00, "category": "Restaurants", "description": "Sushi night", "tags": ["Fun"]},
        ]

        for txn in transactions:
            # Check if transaction already exists to avoid duplicates
            existing_txn = Transaction.query.filter_by(
                date=txn["date"],
                amount=txn["amount"],
                description=txn["description"],
                user_id=user.id
            ).first()
            if not existing_txn:
                transaction = Transaction(
                    date=txn["date"],
                    amount=txn["amount"],
                    category_id=category_dict[txn["category"]].id,
                    description=txn["description"],
                    user_id=user.id
                )
                # Assign tags
                transaction.tags = [tag_dict[tag_name] for tag_name in txn["tags"]]
                db.session.add(transaction)
                print(f"Added transaction: {txn['description']} on {txn['date']}")

        db.session.commit()
        print("All data inserted successfully")

if __name__ == "__main__":
    insert_data()