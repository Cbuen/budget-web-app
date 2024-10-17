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
        with open(jsonData, 'r') as f:
            data = json.load(f)

            # get nested data
            df = pd.DataFrame(data['data'])


        # raw pie chart adding title via html
        fig = px.pie(df, values='Amount', names='Category')

        # Remove chart background
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        chart = fig.to_html(full_html=False)
        return chart

    # Used to READ users raw data and return to JINJA
    @staticmethod
    def userPandaDF(jsonData):
        with open(jsonData, 'r') as f:
            data = json.load(f)

            #Get nested data
            df = pd.DataFrame(data['data'])
        return df

        



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/budget')
def budget():
    chart = DataProcessor.processUserData('app\static\data.json')
    return render_template('budget.html', chart=chart)

@app.route('/editBudget')
def editBudget():
    df = DataProcessor.userPandaDF('app\static\data.json')

    return render_template('editBudget.html', userData=df)

@app.route('/updateBudget', methods=['POST', 'GET'])
def updateBudget():
    update_index = request.form.get('update')
    
    if update_index is not None:
        index = int(update_index)
        new_category = request.form.get(f'category_{index}')
        new_amount = request.form.get(f'amount_{index}')
        
        if new_category and new_amount:
            # Load the current data
            with open('app/static/data.json', 'r') as file:
                data = json.load(file)
            
            # Check if the index is valid
            if 0 <= index < len(data['data']['Category']):
                # Update both category and amount at the specified index
                data['data']['Category'][index] = new_category
                data['data']['Amount'][index] = float(new_amount)
                
                # Save the updated data
                with open('app/static/data.json', 'w') as file:
                    json.dump(data, file, indent=4)
                
                print(f"Updated budget: New Category: {new_category}, New Amount: {new_amount}")
            else:
                print(f"Invalid index: {index}")
        else:
            print(f"Invalid input for index {index}")
    else:
        print("No specific update requested")

    return redirect(url_for('budget'))





"""
import json

# Open and read the file
with open('file.json', 'r') as file:
    data = json.load(file)

# Edit the data
data['new_key'] = 'new_value'

# Save the changes
with open('file.json', 'w') as file:
    json.dump(data, file, indent=4)

"""