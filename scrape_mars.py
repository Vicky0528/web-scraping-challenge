from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests


def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --- Visit Mars News site ---
    browser.visit('https://mars.nasa.gov/news/')

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # Get the first news title
    article = soup.find("div", class_="list_text")
    news_p = article.find("div", class_="article_teaser_body").text
    news_title = article.find("div", class_="content_title").text

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --- Visit JPL site for featured Mars image ---
    browser.visit('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')

    time.sleep(1)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    image = soup.find("img", class_="thumb")["src"]
    img_url = "https://jpl.nasa.gov" + image
    featured_image_url = img_url

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --- Visit Mars Weather Twitter Account ---
    browser.visit('https://twitter.com/marswxreport?lang=en')
    
    time.sleep(1)

    url = "https://twitter.com/marswxreport?lang=en"
    response = requests.get(url)
    bsoup = BeautifulSoup(response.text, "html.parser")

    mars_weather = bsoup.find("div", class_="js-tweet-text-container").text.strip()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    url3 = "http://space-facts.com/mars/"
    browser.visit(url3)

    # Convert table to html
    import pandas as pd
    grab = pd.read_html(url3)
    mars_data = pd.DataFrame(grab[0])
    mars_data.columns = ['Mars', 'Data']
    mars_table = mars_data.set_index("Mars")
    marsdata = mars_table.to_html(classes='marsdata')
    marsdata = marsdata.replace('\n', ' ')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # --- Visit USGS Astrogeology Site ---
    browser.visit('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    
    time.sleep(1)
    
    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    hemi_names = []

    # Search for the names of all four hemispheres
    results = soup.find_all('div', class_="collapsible results")
    hemispheres = results[0].find_all('h3')

    # Get text and store in list
    for name in hemispheres:
        hemi_names.append(name.text)

    # Search for thumbnail links
    thumbnail_results = results[0].find_all('a')
    thumbnail_links = []

    # Iterate through thumbnail links for full-size image
    for thumbnail in thumbnail_results:
        
        # If the thumbnail element has an image...
        if (thumbnail.img):
            
            # then grab the attached link
            thumbnail_url = 'https://astrogeology.usgs.gov/' + thumbnail['href']
            
            # Append list with links
            thumbnail_links.append(thumbnail_url)
    
    full_imgs = []

    for url in thumbnail_links:
        
        # Click through each thumbanil link
        browser.visit(url)
        
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        
        # Scrape each page for the relative image path
        results = soup.find_all('img', class_='wide-image')
        relative_img_path = results[0]['src']
        
        # Combine the reltaive image path to get the full url
        img_link = 'https://astrogeology.usgs.gov/' + relative_img_path
        
        # Add full image links to a list
        full_imgs.append(img_link)

    # Zip together the list of hemisphere names and hemisphere image links
    mars_hemi_zip = zip(hemi_names, full_imgs)

    hemisphere_image_urls = []

    # Iterate through the zipped object
    for title, img in mars_hemi_zip:
        
        mars_hemi_dict = {}
        
        # Add hemisphere title to dictionary
        mars_hemi_dict['title'] = title
        
        # Add image url to dictionary
        mars_hemi_dict['img_url'] = img
        
        # Append the list with dictionaries
        hemisphere_image_urls.append(mars_hemi_dict)
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image_url,
        "weather": mars_weather,
        "mars_facts": marsdata,
        "hemispheres": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data
