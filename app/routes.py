from flask import render_template, request, redirect, url_for, session, jsonify
from app import app
import pandas as pd
import plotly.express as px
import json


class DataProcessor:
    # uses json path as param for function for now until its in the cloud
    # convets json to pandas data frame and creates figure
    @staticmethod
    def processUserData(jsonData):
        with open(jsonData, "r") as f:
            data = json.load(f)

            # get nested data
            df = pd.DataFrame(data["data"])

        # raw pie chart adding title via html
        fig = px.pie(df, values="Amount", names="Category")

        # Remove chart background
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

        chart = fig.to_html(full_html=False)
        return chart

    # Used to READ users raw data and return to JINJA
    @staticmethod
    def userPandaDF(jsonData):
        with open(jsonData, "r") as f:
            data = json.load(f)

            # Get nested data
            df = pd.DataFrame(data["data"])
        return df

    @staticmethod
    def userPandaDFCategory(jsonData):
        with open(jsonData, "r") as f:
            data = json.load(f)

            # Get nested data
            df = pd.DataFrame(data)
        return df

    @staticmethod
    def alignJsonFiles(main_file, categories_file):
        # Load the main JSON file
        with open(main_file, "r") as f:
            main_data = json.load(f)

        # Load the categories JSON file
        with open(categories_file, "r") as f:
            categories_data = json.load(f)

        # Extract categories from main file
        main_categories = set(main_data["data"]["Category"])

        # Update the categories in the categories file
        updated_categories = []
        for category in categories_data["categories"]:
            if category["name"] in main_categories:
                updated_categories.append(category)
                main_categories.remove(category["name"])

        # Add any new categories from the main file
        for new_category in main_categories:
            updated_categories.append(
                {"name": new_category, "amounts": []}  # Initialize with an empty list
            )

        # Update the categories file
        categories_data["categories"] = updated_categories

        # Write the updated data back to the categories file
        with open(categories_file, "w") as f:
            json.dump(categories_data, f, indent=4)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/budget")
def budget():
    chart = DataProcessor.processUserData("app/static/data.json")
    return render_template("budget.html", chart=chart)


@app.route("/spending")
def spending():
    DataProcessor.alignJsonFiles("app/static/data.json", "app/static/categories.json")
    df = DataProcessor.userPandaDFCategory("app/static/categories.json")
    return render_template("spending.html", userData=df)


@app.route("/editBudget")
def editBudget():
    df = DataProcessor.userPandaDF("app/static/data.json")
    return render_template("editBudget.html", userData=df)


@app.route("/goals")
def goals():
    with open("app/static/goals.json", "r") as file:
        userData = json.load(file)
    return render_template("goals.html", userData=userData)


@app.route("/updateGoalName")
def updateGoalName():
    pass


@app.route("/updateGoalAmounts", methods=["POST", "GET"])
def updateGoalAmounts():
    category = request.form["amount"]
    index = int(request.form["index"])
    new_amount = float(request.form["amount"])

    # Load current data
    with open("app/static/goals.json", "r") as file:
        data = json.load(file)

    data["categories"][index]["amount"] = new_amount

    with open("app/static/goals.json", "w") as file:
        json.dump(data, file, indent=4)

    return redirect(url_for("goals"))


@app.route("/removeGoal", methods=["POST", "GET"])
def removeGoal():

    # Load current data
    with open("app/static/goals.json", "r") as file:
        data = json.load(file)

    print(data)

    return redirect(url_for("goals"))


@app.route("/updateBudget", methods=["POST", "GET"])
def updateBudget():
    update_index = request.form.get("update")

    if update_index is not None:
        index = int(update_index)
        new_category = request.form.get(f"category_{index}")
        new_amount = request.form.get(f"amount_{index}")

        if new_category and new_amount:
            # Load the current data
            with open("app/static/data.json", "r") as file:
                data = json.load(file)

            # Check if the index is valid
            if 0 <= index < len(data["data"]["Category"]):
                # Update both category and amount at the specified index
                data["data"]["Category"][index] = new_category
                data["data"]["Amount"][index] = float(new_amount)

                # Save the updated data
                with open("app/static/data.json", "w") as file:
                    json.dump(data, file, indent=4)

    return redirect(url_for("editBudget"))


@app.route("/updateTransaction", methods=["POST"])
def updateTransaction():
    category = request.form["category"]
    index = int(request.form["index"])
    new_amount = float(request.form["amount"])

    # Load current data
    with open("app/static/categories.json", "r") as file:
        data = json.load(file)

    # Update the specific amount
    for cat in data["categories"]:
        if cat["name"] == category:
            cat["amounts"][index] = new_amount
            break

    # Save the updated data
    with open("app/static/categories.json", "w") as file:
        json.dump(data, file, indent=2)

    # Redirect back to the spending page
    return redirect(url_for("spending"))


@app.route("/addBudgetItem", methods=["POST", "GET"])
def addBudgetItem():
    # Load the current data
    with open("app/static/data.json", "r") as file:
        data = json.load(file)

    # Add a new category with default values
    data["data"]["Category"].append("New Category")
    data["data"]["Amount"].append(100.0)  # Default amount of 100

    # Save the updated data
    with open("app/static/data.json", "w") as file:
        json.dump(data, file, indent=4)

    print(f"Added new budget item: Category: New Category, Amount: 100.0")

    return redirect(url_for("editBudget"))


@app.route("/removeBudgetItem", methods=["POST", "GET"])
def removeBudgetItem():
    # LOAD THE CURRENT DATA
    with open("app/static/data.json", "r") as file:
        data = json.load(file)

    # check if there are items to remvoe
    if data["data"]["Category"] and data["data"]["Amount"]:

        # remove last item from both category and amount
        data["data"]["Category"].pop()
        data["data"]["Amount"].pop()

        with open("app/static/data.json", "w") as file:
            json.dump(data, file, indent=4)

        print("Removed last budget item")
    else:
        print("No items to remove")

    return redirect(url_for("editBudget"))


@app.route("/displayTransactions", methods=["POST", "GET"])
def displayTransactions():
    return redirect(url_for("spending"))


@app.route("/addTransaction", methods=["POST", "GET"])
def addTransaction():
    category_index = int(request.form.get("loopIndex"))
    # load the json file
    with open("app/static/categories.json", "r") as file:
        data = json.load(file)

    # add new transaction with defualt amount
    data["categories"][category_index]["amounts"].append(10.0)  # Default amount of 100

    with open("app/static/categories.json", "w") as file:
        json.dump(data, file, indent=4)

    return redirect(url_for("spending"))


@app.route("/removeTransaction", methods=["POST", "GET"])
def removeTransaction():
    category_index = int(request.form.get("loopIndex"))
    with open("app/static/categories.json", "r") as file:
        data = json.load(file)

    if len(data["categories"][category_index]["amounts"]) > 0:
        data["categories"][category_index]["amounts"].pop()
    else:
        print("empty list")
        return redirect(url_for("spending"))

    with open("app/static/categories.json", "w") as file:
        json.dump(data, file, indent=4)

        return redirect(url_for("spending"))
