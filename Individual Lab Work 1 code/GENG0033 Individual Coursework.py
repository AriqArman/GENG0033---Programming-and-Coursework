import pandas as pd
import os
from fuzzywuzzy import fuzz


def createCSV(dataname: str):
    if not os.path.exists(dataname):
        columns = ["Name", "Quantity", "Price", "Additional_Information"]
        df = pd.DataFrame(columns=columns)
        df.to_csv(dataname, index=False, mode='a')

    else:
        df = pd.read_csv(dataname)

    return df

def validateName():
    while True:
        name = input("Enter the name of the item (cannot be solely a number): ").upper()
        if isinstance(name, str) and name.isdigit() == False:
            return name
        else:
            name = input("Enter the name of the item (cannot be solely a number): ").upper()

def validateQuantity():
    while True:
        quantity = input("Enter the quantity of the item (must be a number) : ")
        
        try:
            quantity = float(quantity)
            if quantity > 0:
                return quantity
            else:
                print("Quantity cannot be less than zero!")
            
        except:
            print("Quantity of the item must be a number!")

def validatePrice():
    while True:
        price = input("Enter the price of the item (must be a number) : ")

        try:
            price = float(price)
            if price > 0:
                return price
            else: 
                print("Price cannot be less than zero!")
        except:
            print("Price must be a number!")

def validateIntegerInput():
    while True:
        input_string = input("Enter the index location of the item (must be an integer): ")
        try:
            integer_input = int(input_string)
            return integer_input
        except ValueError:
            print("Enter a whole number")

def additionalInformation():
    new_additional_info = set()
    print("Enter an additional information of an item below. If there are none, press enter")
    additional_info = input("Answer: ").upper()
    new_additional_info.add(additional_info)
    while True:
        cont = input("Do you wish to add more additional information of the item? [Y/N]: ").lower()
        if cont == 'y':
            additional_info = input("Enter the an additional information of an item: ")
            new_additional_info.add(additional_info)
            continue
        elif cont == 'n':
            new_additional_info = ", ".join(new_additional_info)
            return new_additional_info
        else:
            print("Enter either Y or N")
                
def addItem(data: str):
    df = createCSV(data) # create the CSV file if it does not exist
    name = validateName()
    quantity = validateQuantity()
    price = validatePrice()
    additionalInfo = additionalInformation()
    
    df["existing_info"] = df["Name"] + " " + df["Additional_Information"].fillna("") 
    # Calculate similarity score between new row and each existing row
    df["similarity"] = df["existing_info"].apply(\
        lambda x: fuzz.token_set_ratio(x, name + additionalInfo)\
        )
    if df["similarity"].max() >= 90:
        print("This item already exists. If you wish to edit its contents, use the edit feature")
    else:    
        # Append new row to inventory.csv
        new_row = {"Name": name, "Quantity": quantity, "Price": price, "Additional_Information": additionalInfo}
        
        new_df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
        new_df.drop_duplicates(subset=["Name", "Additional_Information"], keep="last", inplace=True)
        new_df.to_csv(data, index=False)
        print(f"Added {name} to {data} with {quantity} quantity and RM{price} price")

def removeItem(data: str) -> pd.DataFrame:
    #input integer location
    df = createCSV(data)

    iloc = validateIntegerInput()
    #Get the information of the item to remove
    item_name = df.loc[int(iloc), "Name"]
    item_qty = df.loc[int(iloc), "Quantity"]
    item_price = df.loc[int(iloc), "Price"]
    if pd.notna(df.loc[int(iloc), "Additional_Information"]):
        item_info = df.loc[int(iloc), "Additional_Information"]

    else:
        item_info = None
    
    #Remove item from inventory
    df.drop(int(iloc), inplace=True)

    #Save updated inventory to CSV file
    df.to_csv('inventory.csv', index= False)

    #Print confirmation message
    print(f"{item_qty} {item_name} priced at {item_price} with additional information of {item_info} has been removed.")

#filter system
def filterSystem(data):
    def filterLogic(data, **kwargs):
        df = createCSV(data)
        df_copy = df.copy()

        for key, value in kwargs.items():
            if value is not None:
                if not df_copy.loc[df_copy[key.title()] == value].empty:
                    df_copy = df_copy.loc[df_copy[key.title()] == value]
                else:
                    print(f"No items matching {key}: {value}")
                    return
        return df_copy
    
    nameCriteria, quantityCriteria, priceCriteria, additionalInformationCriteria = None, None, None, None
    while True:
        print("\nCurrent filter criteria: ")
        print(f"1. Name: {nameCriteria}")
        print(f"2. Quantity: {quantityCriteria}")
        print(f"3. Price: {priceCriteria}")
        print(f"4. Additional Information: {additionalInformationCriteria}")
        print("Apply filter? [Y]")

        choice = input("What would you like to do?: ").lower()
        
        if choice == "1" or choice == "1." or choice == "name":
            nameCriteria = validateName()
        elif choice == "2" or choice == "2." or choice == "quantity":
            quantityCriteria = validateQuantity()
        elif choice == "3" or choice == "3." or choice == "price":
           priceCriteria = validatePrice()
        elif choice == "4" or choice == "4." or choice == "additional information":
            additionalInformationCriteria = validateName()
        elif choice == "y":
            return filterLogic(data, name = nameCriteria, quantity = quantityCriteria, price = priceCriteria, additional_information = additionalInformationCriteria)

    
    
    
def editItem(data: str, iloc: int):
    df = createCSV(data)
    # Get the item information to be edited
    item_to_edit = df.iloc[iloc]

    # Display the current item information
    print(f"Current item information: {item_to_edit['Name']}, {item_to_edit['Quantity']}, {item_to_edit['Price']}, {item_to_edit['Additional_Information']}")

    # Get the new item information from the user
    new_name = validateName()
    new_quantity = validateQuantity()
    new_price = validatePrice()
    new_additional_info = additionalInformation()

    # Check if the new item name and additional information already exist in the CSV file
    if df[(df['Name'] == new_name) & (df['Additional_Information'] == new_additional_info)].shape[0] > 0:
        print("This item already exists in the inventory. No edits made. ")
        return

    # Update the item information in the DataFrame
    df.at[iloc, 'Name'] = new_name
    df.at[iloc, 'Quantity'] = new_quantity
    df.at[iloc, 'Price'] = new_price
    df.at[iloc, 'Additional_Information'] = new_additional_info

    # Save the updated DataFrame to the CSV file
    df.to_csv("inventory.csv", index=False)

    print("Item updated successfully.")
    
def pagingSystem(data) -> bool:
    # show list of all items
    df = createCSV(data)

    # print first 10 items
    print(df.iloc[:10])

    # paging system
    nextPage = input("Next page? (Y/N): ")

    i = 0
    while True:
        if nextPage.capitalize() == 'Y':
            i += 10
            if not df.iloc[i:i+10].empty:
                print(df.iloc[i:i+10])
                nextPage = input("Next page? (Y/N): ")
            else:
                print("No more items to show")
                return True
                
        elif nextPage.capitalize() == 'N':
            return True

        else:
            print("Inputs must be either Y/N")
            nextPage = input("Next page? (Y/N): ")

def clearDF(data):
    #clear the entire dataframe
    while True:
        yesno = input("Are you sure you want to clear the inventory? \nThis cannot be changed later [Y/N]: ").lower()
        if yesno ==  'y':
            os.remove(data)
            df = createCSV(data)
            print(f"Inventory has been cleared")
            return df
        elif yesno == 'n':
            return 
        else:
            print("Enter either Y/N")
    
def userInterface():
    print("\nWelcome to the inventory system!")
    while True:
        dataname = "inventory.csv" #constant
        
        print("\n1. Add item")
        print("2. Edit item")
        print("3. Remove item")
        print("4. Find item")
        print("5. Filter item")
        print("6. Clear system")
        print("7. Quit")

        choice = input("What would you like to do?: ").lower()

        if choice == "1" or choice == "1." or choice == "add item":
            addItem(dataname)

        elif choice == "2" or choice == "2." or choice == "edit item":
            if pagingSystem(dataname) == True:
                iloc = validateIntegerInput()
                editItem(dataname, iloc)

        elif choice == "3" or choice == "3." or choice == "remove item":
            if pagingSystem(dataname) == True:
                removeItem(dataname)

        elif choice == "4" or choice == "4." or choice == "find item":
            pagingSystem(dataname)

        elif choice == "5" or choice == "5." or choice == "filter item":
            if pagingSystem(dataname) == True:
                print(filterSystem(dataname))
                


        elif choice == "6" or choice == "6." or choice == "clear system":
           clearDF(dataname)
           continue

        elif choice == "7" or choice == "7." or choice == "quit":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please choose again.")



userInterface()


