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

@app.route('/editBudget', methods=['GET'])
def editBudget():
    df = DataProcessor.userPandaDF('app\static\data.json')

    return render_template('editBudget.html', userData=df)