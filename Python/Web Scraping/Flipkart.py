## Scraper built for an ongoing project this semester. This scrapes reviews for HP products (printers, laptops, tablets) from http://www.flipkart.com/ ##
## Flipkart is a popular e-commerce site in India, which was the target market for the project ##
## The components that are scraped are Reviews, Review dates, Review ratings and Product names ##
## The output of the scraper will be CSV files for each product category ##

## Each review page contains a maximum of 10 reviews. If there are 200 reviews for a product, then this function will crawl through each of the 20 pages. ##

# Import statements and required packages
from bs4 import BeautifulSoup
import json
import urllib2
import re
import pandas as pd
import string


# Function to scrape flipkart for reviews, starting with a list of product review pages
def flipkart_revs(urls):
    
    # Regular Expressions
    product_regex = re.compile(r'Latest.*(HP.*Notebook|HP.*Printer|HP.*Tab[let]?).*')
    count_regex = re.compile(r'\d{1,5}')
    rating_regex = re.compile(r'[0-9]')
    
    # List initializations
    dates_list = []
    reviews_list = []
    products_list = []
    ratings_list = []
    
    # Loop to open each page in list of links
    for url in urls:
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        
        # Retrieve product name and count of product reviews
        product = str(re.findall(product_regex,soup.find("head").title.contents[0])[0])
        num_revs = int(re.findall(count_regex,soup.find("span",{"class":"fk-font-normal unboldtext"}).text)[0])
        if num_revs % 10 == 0:
            new_num_revs = num_revs + 1
            
        products = [product]*num_revs
        products_list.extend(products)
        
        reviews = []
        ratings = []
        dates = []
        
        # Determine appropriate number of pages to scrape based on count of product reviews
        if num_revs % 10 == 0:
            rev_nums = range(0,new_num_revs,10)
        else:
            rev_nums = range(0,num_revs,10)
        
        # Crawl through each page of reviews for a product and scrape
        for i in rev_nums:
            iter_page = urllib2.urlopen(url+"&sort=most_helpful&start="+str(i))

            # Keep track of progress, printin line for each new page being scraped
            print("Scraping %s page %s" % (product,str((i/10)+1)))
            
            soup_iter = BeautifulSoup(iter_page)

            for review in soup_iter.findAll("span",{"class": "review-text"}):
                reviews.append(review.text)

            for rating in soup_iter.findAll("div",{"class":"fk-stars"}):
                ratings.append(re.findall(rating_regex,rating.get("title"))[0])

            for date in soup_iter.findAll("div",{"class":"date line fk-font-small"}):
                clean_date = date.text.strip()
                date_parts = clean_date.split()
                dates.append('-'.join(date_parts))

        # Clean text and remove ASCII/Unicode characters with string.printable
        reviews = [filter(lambda x: x in string.printable, reviews[i]) for i in range(len(reviews))]
        reviews = [str(review).strip() for review in reviews]
        reviews = [review.replace("\n"," ") for review in reviews]

        reviews_list.extend(reviews)
        dates_list.extend(dates)
        ratings_list.extend(ratings)
    
    # Create dictionary to prepare for quick and easy conversion to pandas dataframe
    HP_flip_dict = {}
    HP_flip_dict['Products'] = products_list
    HP_flip_dict['Reviews'] = reviews_list
    HP_flip_dict['Dates'] = dates_list
    HP_flip_dict['Ratings'] = ratings_list
    
    return HP_flip_dict


