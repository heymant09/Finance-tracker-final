from datetime import datetime

CATEGORIES = {'I':"income",'E':"expense"}
''' this file is creatd so we have a place where we can write all of 
the functions related to getting information of the user '''

def get_date(prompt, allow_default=False):
        date_str = input(prompt)
        # if the user wants to give todays date he can simply press enter
        if allow_default and not date_str:
                return datetime.today().strftime("%d-%m-%Y")
        
        try:
                valid_date = datetime.strptime(date_str,"%d-%m-%Y")
                return valid_date.strftime("%d-%m-%Y")
        except ValueError:
                print("Invalid date format. format -> (dd-mm-yyyy)")
                return get_date(prompt,allow_default)
        

def get_amount():
        try:
                amount = float(input("Enter the Amount: "))
                if amount <= 0:
                        raise ValueError("Amount can't be negative nor Zero")
                return amount
        except ValueError as e:
                print(e)
                return get_amount()

def get_category():
        category = input("Enter catgory ('I' for income or 'E' for expense: ").upper()
        if category in CATEGORIES:
                return CATEGORIES[category]
        print("Invalid category")
        return get_category()

def get_description():
        return input("Enter a description (Optional): ") 