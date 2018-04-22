from flask import Flask, jsonify, render_template, redirect
import pymongo
from flask_pymongo import PyMongo
import scrape_mars
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd


app = Flask(__name__)
mongo = PyMongo(app)

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars_db
collection = db.items

@app.route('/')
def index():
    scrape_dict = mongo.db.scrape_dict.find_one()
   # scrape_dict = list(db.collection.find())
    #print(mars)
    return render_template('index.html', scrape_dict=scrape_dict)


@app.route("/scrape")
def scrape():
    scrape_dict = mongo.db.scrape_dict
    scraped_data = scrape_mars.scrape()
    scrape_dict.update(
        {},
        scraped_data,
        upsert=True
    )
    return redirect("http://localhost:5000/", code=302)



if __name__ == "__main__":
    app.run(debug=True)