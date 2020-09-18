
from bs4 import BeautifulSoup as bs
import os
import requests
import pandas as pd
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import urllib.request
import urllib.parse
import shutil

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    #Dictionary to collect data
    mars = {}

    #### Title image####
    dream = 'static/images/mission_to_mars.png'
    mars["dream"] = dream

    #### Latest NASA Mars News Story####

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(response.text, 'lxml')

    # Put together link to top story
    link = [a['href'] for a in soup.select("a[href*=news]")][0]
    base = "https://mars.nasa.gov/news"
    url = urllib.parse.urljoin(base,link)

    # Fetch headline and text  
    browser.visit(url)
    news_title = browser.find_by_tag('h1').value
    news_p = browser.find_by_css('div[id="primary_column"]').text
    news_p = news_p.replace('\n', ' ')

    # Add title and text to data dictionary 
    mars["news_title"] = news_title
    mars["news_p"] = news_p

    #### JPL Mars Space Images - Featured Image ####
 
    # Visit site and make soup
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    response = requests.get(url)
    soup = bs(response.text, 'lxml')

    #Get image 
    partial_address = soup.find_all('a', class_='fancybox')[1].get('data-fancybox-href').strip()
    base = "https://www.jpl.nasa.gov"
    featured_image_url = urllib.parse.urljoin(base, partial_address)

    #Get brief image description
    image_description = soup.find_all('a', class_='fancybox')[1].get('data-description').strip()

    #Add url and description to dictionary
    mars["featured_image_url"] = featured_image_url    
    mars["image_description"] = image_description
    
    #### Mars Facts

    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    mars_facts_df = tables[0]
    mars_facts_html_table = mars_facts_df.to_html(header=False, border=False, index=False)
    mars_facts_html_table = mars_facts_html_table.replace('\n', '')
    mars["table"] = mars_facts_html_table 

    #### Mars Hemispheres

    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    # Retrieve page with the requests module
    response = requests.get(url)

    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(response.text, 'lxml')

    #Find titles and links for full-scale images and information pages
    base = "https://astrogeology.usgs.gov"
    hemisphere_image_urls = []
    thumbnail_urls = []

    for link in soup.find_all(class_='itemLink product-item'):
        partial = link.get('href')   
        thumbnail_url = urllib.parse.urljoin(base, partial)
        browser.visit(thumbnail_url)
        xpath = "//a[@class='open-toggle']"
        switch = browser.find_by_xpath(xpath)
        switch.click()
        html = browser.html
        soup = bs(html, 'lxml')
        title = soup.find(class_ = 'title').get_text()
        images=browser.find_by_xpath('/html/body/div[1]/div[1]/div[2]/img')  
        img_url =  images["src"]  
        thumbnail_urls.append({'title':title, 'thumbnail_url':thumbnail_url})
        hemisphere_image_urls.append({'title':title, 'img_url':img_url})
    browser.quit()
    mars["hemisphere_image_urls"] = hemisphere_image_urls
    mars["thumbnail_urls"] = thumbnail_urls

    return mars