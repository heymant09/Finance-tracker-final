import pandas as pd
import csv
from datetime import datetime
from data_entry import get_amount,get_category,get_date,get_description
import matplotlib.pyplot as plt

class CSV:
        #COLUMN & CSV_FILE are Constant,will be replace by it's value whenever and wherever it's used
        CSV_FILE = "finance_data.csv"
        COLUMNS = ["date","amount","category","description"]
        FORMAT = "%d-%m-%Y"
        
        @classmethod # Decorator
        #initialize CSV Function either reads the CSV or Creates one if it doesn't alreadt exist
        def initialize_csv(cls): 
                try:
                        pd.read_csv(cls.CSV_FILE)
                except FileNotFoundError:
                        df = pd.DataFrame(columns=cls.COLUMNS)
                        df.to_csv(cls.CSV_FILE, index=False)
        
        @classmethod
        def add_entry(cls,date,amount,category,description):
                # A dictionary to store our user input
                new_entry = {
                        "date" : date,
                        "amount" : amount,
                        "category": category,
                        "description": description,
                }
                with open(cls.CSV_FILE,"a",newline="") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
                        writer.writerow(new_entry)
                print("Entry added successfully")
                
        @classmethod
        # Method to fetch transactions in a particular time period
        def get_transactions(cls, start_date, end_date):
                # We need a dataframe first
                df = pd.read_csv(cls.CSV_FILE)
                # Using pandas dataframe we convert Dates from string to datetime object
                df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
                # converting to datetime object from user input string value
                start_date = datetime.strptime(start_date, CSV.FORMAT)
                end_date = datetime.strptime(end_date, CSV.FORMAT)
                #Now that they're no longer string, we can compare thm
                
                # Now we need to create a mask which gives filter data according to giveen condition
                # we are able to compare dates because they're now a datetime object
                mask = (df["date"] >= start_date) & (df["date"] <= end_date)
                
                filtered_df = df.loc[mask] #df.loc helps us filter by label
                
                if filtered_df.empty:
                        print("No transactions in the give time period")
                else:
                        print(
                                f"Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}"
                        )
                        print(
                                filtered_df.to_string(
                                        index=False, formatters= {"date": lambda x: x.strftime(CSV.FORMAT)}
                                        # what we have written above is a lambda function read about it
                                )
                        )
                        
                        total_income = filtered_df[filtered_df["category"] == 'income']["amount"].sum()
                        total_expense = filtered_df[filtered_df["category"] == 'expense']["amount"].sum()
                        print("\nSummary: ")
                        print(f"Total income: Rupees {total_income:.2f}")
                        print(f"Total expense: Rupees {total_expense:.2f}")
                        print(f"Net Savings: Rupees {(total_income - total_expense):.2f}")
                        
                return filtered_df        
def add():
        CSV.initialize_csv()
        date = get_date("Enter date of transaction (dd-mm-yyyy), Press Enter for todays date: ",
                        allow_default=True,
        )
        amount = get_amount()
        category = get_category()
        description = get_description()
        CSV.add_entry(date,amount,category,description)

def plot_transactions(df):
        df.set_index("date", inplace=True)
        # This is to get the dataframe with all the dates of income
        income_df = (
                df[df["category"] == 'income']
                .resample("D")
                .sum()
                .reindex(df.index,fill_value=0)
        )
        # This one is same but for expense
        expense_df = (
                df[df["category"] == 'expense']
                .resample("D")
                .sum()
                .reindex(df.index,fill_value=0)
        )
        # Now we need to plot the graph for which we're gonna use Matplot lib

        plt.figure(figsize=(10,5))
        # Now we can plot where index is date acting as X-axis and amount as Y-axis
        plt.plot(income_df.index,income_df["amount"], label="Income", color="g")
        plt.plot(expense_df.index,expense_df["amount"], label="Expense", color="r")
        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.title("Income and Expense Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()
        
def main():
        while True:
                print("\n1. Add a new transaction")
                print("2. View transaction summary within date range")
                print("3. Exit")
                
                choice = input("Enter your choice (1-3): ")
                
                if choice == "1":
                        add()
                elif choice == "2":
                        start_date = get_date("Enter start date: ")
                        end_date = get_date("Enter end date: ")
                        df = CSV.get_transactions(start_date,end_date)
                        
                        if(input("Do you want to see a graph plot of transactions? (Y/N) ").lower() == 'y'):
                              plot_transactions(df) 
                              
                elif choice == "3":
                        print("Have a nice day. Bye...")
                        break
                else:
                        print("invalid choice. Enter 1, 2, 3. ")
                        
if __name__ == "__main__":
        main()                        