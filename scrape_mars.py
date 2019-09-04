from splinter import Browser
from bs4 import BeautifulSoup 

import pandas as pd
import re

mars_data = {}

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    news_url = 'https://mars.nasa.gov/news/'
    mar_image_jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    mars_weather_url = 'https://twitter.com/marswxreport?lang=en'
    mars_fact_url = 'http://space-facts.com/mars/'

    # The link https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars is not available
    # Using this link instead. 
    mars_hemi_pics_url = 'http://www.planetary.org/blogs/guest-blogs/bill-dunford/20140203-the-faces-of-mars.html'
    
    
    # create mars_data dict that we can insert into mongo
    
    mars_data = {}
    # NASA Mars News
    browser.visit(news_url)
    
    #Important: waiting for loading the paging...
    browser.is_element_present_by_value('article_teaser_body', wait_time=5)

    news_html = browser.html
    news_bs = BeautifulSoup(news_html,'html.parser')
    
    news_title = news_bs.find('div', attrs={'class':'content_title'}).text
    news_p = news_bs.find('div', attrs={'class':'article_teaser_body'}).text

    mars_data['news_title'] = news_title
    mars_data['news_p'] = news_p
    
    # JPL Mars Space Images - Featured Image

    browser.visit(mar_image_jpl_url)
    img_html = browser.html
    img_bs = BeautifulSoup(img_html,'html.parser')

    feature_img = img_bs.find('article',attrs={'class':'carousel_item'})
    feature_img_url_string = feature_img['style']
    featured_image_link = re.findall(r"'(.*?)'",feature_img_url_string)
    featured_image_link = 'https://www.jpl.nasa.gov'+ featured_image_link[0]

    mars_data['featured_img_link'] = featured_image_link

    # Mars Weather
    browser.visit(mars_weather_url)
    weather_html = browser.html
    weather_bs = BeautifulSoup(weather_html,'html.parser')
    mars_weather = weather_bs.find('div', attrs={'class':'js-tweet-text-container'}).find('p').text 
    mars_weather = mars_weather.replace('pic.twitter.com',' ').rsplit(' ',1)[0]

    mars_data['weather'] = mars_weather

    # Mars Facts
    mars_facts_table = pd.read_html(mars_fact_url)
    mars_facts_df = mars_facts_table[0]
    mars_facts_df.columns = ['Description','Value']
    mars_facts_df.set_index('Description',inplace=True) 

    mars_facts_html = mars_facts_df.to_html()

    mars_data['facts'] = mars_facts_html

    # Mars Hemispheres
    browser.visit(mars_hemi_pics_url)
    hemi_html = browser.html
    hemi_bs = BeautifulSoup(hemi_html,'html.parser')

    mars_hemi_img_links = hemi_bs.find_all('img',attrs={'class':'img840'})
    hemisphere_image_urls =[]

    for each_img in mars_hemi_img_links:
        title = each_img.attrs['alt']
        url = each_img.attrs['src']
        hemisphere_image_urls.append({'title':title,'img_url':url})

    mars_data['hemi_img'] = hemisphere_image_urls


    browser.quit()
    return mars_data