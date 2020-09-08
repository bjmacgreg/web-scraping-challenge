
import pymongo
from bs4 import BeautifulSoup as bs
import os
import requests
import pandas as pd
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import urllib.request
import urllib.parse
import re

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", usr/local/bin/chromedriver, headless=False)

def scrape():
    # ### NASA Mars News

    # Initialize PyMongo to work with MongoDBs
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)

    # Define database and collection
    db = client.NASA_Mars_news_db
    stories = db.stories

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'

    # Retrieve page with the requests module
    response = requests.get(url)

    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(response.text, 'lxml')
    #print(soup.prettify)

    # Examine the results, then determine element that contains sought info
    # results are returned as an iterable list

    results = soup.find_all(class_='slide')
    #results

    # Loop through returned results

    for result in results:
        try:
            news_title = result.find('div', class_="content_title").get_text()
            news_p = result.find('div', class_="rollover_description_inner").get_text()
            if (news_title and news_p):
                print ('-------------')
                print (news_title)
                print (news_p)
            # Dictionary to be inserted as a MongoDB document
                post = {
                    'news_title': news_title.strip(),
                    'news_p': news_p.strip()
                }
                stories.insert_one(post)
                print(post)
        except Exception as e:
            print(e)
            
    #print(stories)

    NASA_news = db.stories.find()

    #for article in NASA_news:
    #    print(article)


    # ### JPL Mars Space Images - Featured Image


    # Thanks to GitHub for the fancybox help, I was really stuck. Didn't realize "fancybox" could be a class. 
    #https://github.com/ZL14E161110/HW13---Web-Scraping-and-Document-Databases
    #Didn't look at the rest of it, although I'm sure it's brilliant. 

    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'lxml')

    #Assuming the latest Mars image will always be the one in the first position of the grid...
    #Note 0 is the overall featured image, which is not necessarily of Mars.

    partial_address = soup.find_all('a', class_='fancybox')[1].get('data-fancybox-href').strip()
    base = "https://www.jpl.nasa.gov"
    featured_image_url = urllib.parse.urljoin(base, partial_address)
    #featured_image_url
    browser.quit()

    # ### Mars Facts

    url = 'https://space-facts.com/mars/'

    tables = pd.read_html(url)
    type(tables)

    tables[0]

    mars_facts_df = tables[0]
    mars_facts_df.set_index([0], inplace=True)
    #mars_facts_df

    mars_facts_df.rename(columns=mars_facts_df.iloc[0]).drop(mars_facts_df.index[0])
    #mars_facts_df

    mars_facts_html_table = mars_facts_df.to_html()
    mars_facts_html_table = mars_facts_html_table.replace('\n', '')
    #mars_facts_html_table
    #print(mars_facts_html_table)

    ###Make sure extra header row is gone###


    # ### Mars Hemispheres

    #navigate to starting page
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    browser = Browser("chrome", **executable_path, headless=False)
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    #Make soup
    # Retrieve page with the requests module
    response = requests.get(url)

    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(response.text, 'lxml')
    #print(soup.prettify)

    #Find titles and links for full-scale images

    title_list = []
    img_url_list = []
    base = "https://astrogeology.usgs.gov"

    for link in soup.find_all(class_='itemLink product-item'):
        partial = link.get('href')    
        thumbnail_url = urllib.parse.urljoin(base, partial)
        browser.visit(thumbnail_url)
        xpath = "//a[@class='open-toggle']"
        switch = browser.find_by_xpath(xpath)
        switch.click()
        html = browser.html
        soup = bs(html, 'lxml')
        imgs = soup.find(class_='downloads')
        html = browser.html
        soup = bs(html, 'lxml')
        title = soup.find(class_ = 'title').get_text()
        img_url = [a['href'] for a in soup.select('a:contains(Original)')]
        title_list.append(title)
        img_url_list.append(*img_url)
    #    print(title, *img_url)
    browser.quit()
    hemisphere_image_urls = zip(title_list, img_url_list)


















# ## Step 2 - MongoDB and Flask Application
# 
# Use MongoDB with Flask templating to create a new HTML page that displays all of the information that was scraped from the URLs above.
# 
# * Start by converting your Jupyter notebook into a Python script called `scrape_mars.py` with a function called `scrape` that will execute all of your scraping code from above and return one Python dictionary containing all of the scraped data.
# 
# * Next, create a route called `/scrape` that will call your `scrape_mars.scrape` function. Note that you'll have to import `scrape_mars.py`. 
# 
#   * Store the dictionary that gets returned to your MongoDB.
# 
# * Create an index route `/` that will query your Mongo database and pass the Mars data into an HTML template to be displayed. 
# 
# * Create a template HTML file called `index.html` that will take the dictionary of Mars data and display its values in the appropriate HTML elements. Use the following as a guide for what the final product should look like, but feel free to create your own design.
# 
# ![final_app_part1.png](Images/final_app_part1.png)
# ![final_app_part2.png](Images/final_app_part2.png)
