from flask import Flask, redirect, url_for, request, render_template
import pickle
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import chart_studio.plotly as py
import plotly.graph_objects as go
from IPython.display import HTML
import plotly.express as px
from preprocessing import getdataset
from scraping import get_rsi, get_nse_rsi
import pickle

from scraping import company_dict

# Sendgrid API
import sendgrid
import os
from sendgrid.helpers.mail import *
sg = sendgrid.SendGridAPIClient('SG.s3zLZHNZR0uH4sHoVNSj6A.SmX4nNLxn-jCmHxl1ZkxqOmGQk4XkqY7CY0V1wnkIK4')

  
pickle_dict = {
    'Axis': 'pikl_files/Axis.pkl',
    'Cipla': 'pikl_files/Cipla.pkl',
    'HCL':'pikl_files/HCL.pkl',
    'HDFC Bank':'pikl_files/HDFC.pkl',
    'Hindustan Unilever': 'pikl_files/Hindunilvr.pkl',
    'Infosys': 'pikl_files/Infosys.pkl',
    'ITC': 'pikl_files/ITC.pkl',
    'JSW Steel': 'pikl_files/jswsteel.pkl',
    'ONGC': 'pikl_files/Ongc.pkl',
    'Reliance': 'pikl_files/Reliance.pkl',
    'TATA Consultancy Services': 'pikl_files/TCS.pkl',
    'Tech Mahindra': 'pikl_files/Techm.pkl',
    'Wipro': 'pikl_files/Wipro.pkl',
    'UPL': 'pikl_files/UPL.pkl'
}

#email = user_input

df50 = getdataset()

with open('classifier.pkl', 'rb') as file:
    nifty_pickle = pickle.load(file)
    
app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/trend', methods=['GET'])
def trend():
    return render_template("trend.html")


@app.route('/trend', methods=['POST'])
def detect_trend():
    
    company = request.form['company']

    company_url = company_dict.get(company)

    uemail = request.form['uemail']

    from_email = Email("stockforecasting21@gmail.com")
    to_email = To(uemail)
    subject = "Stock Prediction Result"
    

    if company == 'NIFTY 50':
        rsi, macd, roc = get_nse_rsi()
        prediction = nifty_pickle.predict([[rsi, macd, roc]])
    else:
        rsi, macd, roc = get_rsi(company)
        
        pickle_file = pickle_dict.get(company)
        with open(pickle_file, 'rb') as file:
            company_pickle = pickle.load(file)
        
        prediction = company_pickle.predict([[rsi, macd, roc]])
        
    
    trend_value=str(prediction).strip('[]')
    if trend_value=='1':
        trend ='Uptrend'
        #email send
        html_content = '<div style="padding:40px;">\
                            <h1> <i class="far fa-chart-bar"></i>  Stock Prediction</h1>\
                            <h2>' + company + ' is ' + trend + '</h2>\
                            <center> <a style="text-decoration: none; color: white; padding: 20px; border: 1px solid white; background-color: #0A80FB;" href='+ company_url +'>View Stock</a> <center>\
                        </div>'
        content = Content("text/html", html_content)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())

    else:
        trend = 'Downtrend'

        html_content = '<h2 style="color: red">' + company + ' is ' + trend + '</h2>'
        content = Content("text/html", html_content)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())

    return render_template('predict.html', rsi=rsi, trend=trend,macd=macd, roc=roc, company=company, uemail=uemail)



@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    fig=px.line(df50, x='Date',y='Open', title='Nifty 50 Closing Price vs Date', width=800, height=400)
    image = HTML(fig.to_html())
    return render_template("visualize.html",image=image)

@app.route('/projectlink', methods=['GET', 'POST'])
def projectlink():
    project_link = 'https://github.com/Pandani07/Final-Project'
    return render_template("projectlink.html", project_link = project_link)

if __name__ == "__main__":
    app.run(debug=True)