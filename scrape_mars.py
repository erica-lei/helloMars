#notes : I run it and my results are added onto MongoDB
#However, I get error on /scrape
#I can't pull data with my facts on mongodb

#import dependencies
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from flask_pymongo import PyMongo
import pandas as pd
from flask import Flask, jsonify, render_template
from env import path
from splinter import Browser


# app = Flask(__name__)
# mongo = PyMongo(app)

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars_db
collection = db.items



def init_browser():
    executable_path = {"executable_path": path}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    scrape_dict = {}
    nasa_url = "https://mars.nasa.gov/news/"
    browser.visit(nasa_url)
    nasa_html = browser.html
    nasa_soup=bs(nasa_html, 'html.parser')
    titles = []
    results = nasa_soup.find_all('div',class_="content_title")  
    latest_title=results[0].text
    scrape_dict["latest_title"] = latest_title
    paragraph = []
    paras = nasa_soup.find_all('div', class_='rollover_description_inner')
    latest_paragraph = paras[0].text
    scrape_dict["latest_paragraph"] = latest_paragraph
    featured_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(featured_image)
    mars_browser = browser.html
    featured_mars=bs(mars_browser,'html.parser')
    featured_path = featured_mars.find("a","fancybox")["data-fancybox-href"]
    jpl_link = "https://www.jpl.nasa.gov/" + featured_path
    scrape_dict["jpl_link"]= jpl_link

    twitter_url = "https://twitter.com/marswxreport?lang=en"
    weather_response = requests.get(twitter_url)
    weather_tweets = bs(weather_response.text,"html.parser")
    #first weather tweet for mars 
    latest_weather = weather_tweets.find_all("p",class_="TweetTextSize")[0].text.strip()
    scrape_dict["latest_weather"] = latest_weather
    #mars facts
    facts_url = "https://space-facts.com/mars/"
    facts_response = requests.get(facts_url)
    facts_soup = bs(facts_response.text,"html.parser")
    table = facts_soup.find_all('table')[0]
    facts_list = pd.read_html(str(table))[0]
    df = facts_list.rename(index = str, columns={0:"Description", 1:"Facts"})
    html_table = df.to_html()
    scrape_dict["facts_table"] = html_table

    #hemispheres
    # link_pic1 = "https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced"
    # cerberus_response = requests.get(link_pic1)
    # cerberus_soup = bs(cerberus_response.text,"html.parser")
    # cerberus_soup.find_all("img",class_="wide-image")
    # cerberus_img = "https://astrogeology.usgs.gov/cache/images/cfa62af2557222a02478f1fcd781d445_cerberus_enhanced.tif_full.jpg"
    # scrape_dict["cerberus_img"] = cerberus_img
    link_pic1 = "https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced"
    browser.visit(link_pic1)
    link1 = browser.html
    html_link1 = bs(link1,'html.parser')
    cer_hem = html_link1.find("img", class_="wide-image")["src"]
    astrogeology_url = "https://astrogeology.usgs.gov/"
    cerberus_png = astrogeology_url + cer_hem
    scrape_dict["cerberus_png"] = cerberus_png

    link_pic2 = "https://astrogeology.usgs.gov/search/map/Mars/Viking/schiaparelli_enhanced"
    browser.visit(link_pic2)
    link2 = browser.html
    html_link2 = bs(link2, 'html.parser')
    sch_hem = html_link2.find("img", class_="wide-image")["src"]
    schiaparelli_png = astrogeology_url + sch_hem
    scrape_dict["schiaparelli_png"] = schiaparelli_png

    link_pic3= "https://astrogeology.usgs.gov/search/map/Mars/Viking/syrtis_major_enhanced"
    browser.visit(link_pic3)
    link3 = browser.html
    html_link3 = bs(link3, 'html.parser')
    syrt_hem = html_link3.find("img", class_="wide-image")["src"]
    syrtis_png = astrogeology_url + syrt_hem
    scrape_dict["syrtis_png"] = syrtis_png
   
    link_pic4= "https://astrogeology.usgs.gov/search/map/Mars/Viking/valles_marineris_enhanced"
    browser.visit(link_pic4)
    link4 = browser.html
    html_link4 = bs(link4, 'html.parser')
    valles_hem = html_link4.find("img", class_="wide-image")["src"]
    valles_png = astrogeology_url + valles_hem
    scrape_dict["valles_png"] = valles_png
    

    hemisphere_image_urls = [
        {"title":"Cerberus Hemisphere","img_url":cerberus_png},
        {"title":"Schiaparelli Hemisphere","img_url":schiaparelli_png},
        {"title":"Syrtis Major","img_url":syrtis_png},
        {"title":"Valles Marineris","img_url":valles_png}    
    ]
 
    scrape_dict["hemisphere_image_urls"] = hemisphere_image_urls

    #links for faces
    # face_links_mars = []
    # for i in scrape_dict["hemisphere_image_urls"]:
    #     face_links_mars.append(i['img_url'])
    # mf1 = face_links_mars[0]
    # scrape_dict["mf1"] = mf1
    # mf2 = face_links_mars[1]
    # scrape_dict["mf2"] = mf2
    # mf3 = face_links_mars[2]
    # scrape_dict["mf3"] = mf3
    # mf4 = face_links_mars[3]
    # scrape_dict["mf4"] = mf4


    collection.insert_one(scrape_dict)


    return scrape_dict


def index():
    mars = list(db.collection.find())
    print(mars)
    return render_template('index.html', mars = mars)


