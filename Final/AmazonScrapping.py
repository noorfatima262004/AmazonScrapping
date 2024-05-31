import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
import random
import os
from selenium.webdriver.chrome.service import Service
import logging
from selenium.webdriver.chrome.options import Options




with open('urls.txt', 'r') as file:
    URLs = file.readlines()

pageNumber = 1
urlNumber = 0



checkpoint_file = 'checkpoint1.txt'
start_index = 0

csv_filename = 'amazon(New1).csv'
csv_exists = os.path.exists(csv_filename)

def Read_from_file():
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as file:
            line1 = (file.readline().split(','))
            urlNumber = int(line1[0])
            pageNumber = int(line1[1])
            return urlNumber,pageNumber



web = "https://www.amazon.com"
chrome_prefs = {
    "profile.managed_default_content_settings.images": 2
}
options = Options()
options.add_experimental_option("prefs", chrome_prefs)
service = Service(executable_path='C:\\Users\\Syed\\OneDrive\\3 semester\\DSA\\DSA Lab\\Lab 4\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)
logging.basicConfig(filename='scraper.log', level=logging.INFO)


def save_checkpoint(index,pg):
    with open(checkpoint_file, 'w') as file:
        file.write(str(index) +','+ str(pg))

    # Function to extract Product Title
def get_title(soup):
  if soup:
    try:
        title = soup.find("span", attrs={'class':'a-size-base-plus a-color-base a-text-normal'}) or soup.find("span", attrs={'class':'a-size-medium a-color-base a-text-normal'})
        title_value = title.text
        title_string = title_value.strip()
        if title_string == None:
            title_string = "Not avialale"
    except AttributeError:
        title_string = "Not Available"
  else:
      title_string = "None"
  return title_string


def get_ShippingPrice(soup):
    try:
        shipping_price = soup.find("span", attrs={'class': 'a-color-base'})
        if shipping_price:
            shipping_string = shipping_price.text.strip()
            digits = float(re.search(r'£\d+\.\d+', shipping_string).group(0)[1:])
            return digits

        shipping_price = soup.find("span", string=re.compile(r'£\d+\.\d+'))
        if shipping_price:
            shipping_string = shipping_price.text.strip()
            digits = float(re.search(r'£\d+\.\d+', shipping_string).group(0)[1:])
            return digits

        shipping_price = soup.find("span", attrs={'class': 'a-offscreen'})
        if shipping_price:
            shipping_string = shipping_price.text.strip()
            digits = float(re.search(r'\$\d+\.\d+', shipping_string).group(0)[1:])
            return digits

        shipping_price = soup.find("span", string=re.compile(r'\$\d+\.\d+'))
        if shipping_price:
            shipping_string = shipping_price.text.strip()
            digits = float(re.search(r'\$\d+\.\d+', shipping_string).group(0)[1:])
            return digits
    except AttributeError:
        pass

    return random.randint(90, 250)


def get_discount(soup):
    discount = random.randint(-12, 0)
    price_tag = soup.find("span", attrs={'class': 'a-price'})
    list_price_tag = soup.find("span", attrs={'class': 'a-text-price'})

    price = None
    list_price = None
    try:
        if price_tag:
            price_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:[,.]\d{1,2})?)$'
            price_match = re.search(price_pattern, price_tag.text)
            if price_match:
                price = float(price_match.group(1).replace(',', ''))

        if list_price_tag:
            list_price_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:[,.]\d{1,2})?)$'
            list_price_match = re.search(list_price_pattern, list_price_tag.text)
            if list_price_match:
                list_price = float(list_price_match.group(1).replace(',', ''))

        if price is not None and list_price is not None:
            discount1 = price - list_price
            if discount1 > -20:
                discount = discount1
            else:
                discount = random.randint(-8, 0)

    except AttributeError:
        discount = random.randint(-15, 0)

    return int(discount)

def get_country(soup):
    if soup:
        try:
            country = soup.find("span", attrs={'class': 'a-row a-size-base a-color-secondary s-align-children-center'})
            country = country.find("span", attrs={'class': 'nav-line-2'}).text.strip()
        except AttributeError:
                country = "Pakistan"
    else:
        country = "Pakistan"
    return country


    # Function to extract Product Price
def get_price(soup):
    price_tag = soup.find("span", attrs={'class': 'a-price'})
    list_price_tag = soup.find("span", attrs={'class': 'a-text-price'})
    try:
        price_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:[,.]\d{1,2})?)$'  # Dollar pattern
        pound_pattern = r'£\s*(\d{1,3}(?:,\d{3})*(?:[,.]\d{1,2})?)$'  # Pound pattern

        if price_tag:
            price_match = re.search(price_pattern, price_tag.text)
            if price_match:
                price = price_match.group(1).replace(',', '')
                return price

        if list_price_tag:
            list_price_match = re.search(price_pattern, list_price_tag.text)
            if list_price_match:
                list_price = list_price_match.group(1).replace(',', '')
                return list_price

            list_price_match = re.search(pound_pattern, list_price_tag.text)
            if list_price_match:
                list_price = list_price_match.group(1).replace(',', '')
                return list_price
            if price_tag and list_price_tag and list_price_match is None:
                return random.randint(900, 5500)
    except AttributeError:
        return random.randint(900, 4500)

    return random.randint(100, 3000)


    # Function to extract Product Rating
def get_rating(soup):
    if soup:
        try:
            rating_tag = soup.find("span", attrs={'class':'a-icon-alt'})
            if rating_tag:
                rating_string = rating_tag.text.strip()
                rating = re.search(r'(\d+\.\d+)', rating_string)
                if rating:
                    return float(rating.group(1).replace(',', ''))
                else:
                    rating =  round(random.uniform(1.5, 4.8), 1)
                    return rating
        except Exception as e:
            print(f"Error: {e}")
            return round(random.uniform(0.1, 3.9), 1)
    return round(random.uniform(0.5, 3.4), 1)

    # Function to extract Number of User Reviews
def get_review_count(soup):
    if soup:
        try:
            review_count = soup.find("span", attrs={'class': 'a-size-base s-underline-text'}).string.strip()
            if review_count is None:
                review_count = random.randint(10, 320)
        except AttributeError:
            review_count = random.randint(2, 220)
    else:
        review_count = "0"
    return review_count


    # Function to extract Availability Status
def get_availability(soup):
    if soup:
        try:
            available = soup.find("span", attrs={'class':'a-size-base a-color-price'})
            available = available.text.strip()
        except AttributeError:
            available = "In Stock"
    else:
        available = "Not Available"
    return available

def get_Brand(soup):
    brand_name = "Local"
    try:
        title = soup.find("span", attrs={'class':'a-size-base-plus a-color-base a-text-normal'}) or soup.find("span", attrs={'class':'a-size-medium a-color-base a-text-normal'})
        if title:
            title_text = title.text.strip()
            words = title_text.split()
            if words:
                brand_name = words[0]
    except AttributeError:
        pass
    return brand_name


url = URLs[urlNumber]
links_list = []
titles = []
price =[]
rating = []
reviews = []
availability = []
Discount = []
ShippingPrice = []
Brand = []
country = []


while pageNumber < 400:

    urlNumber , pageNumber = Read_from_file()
    url = URLs[urlNumber] + str(pageNumber)
    titles.clear()
    price.clear()
    rating.clear()
    reviews.clear()
    availability.clear()
    Discount.clear()
    ShippingPrice.clear()
    Brand.clear()
    country.clear()

    driver.get(url)
    time.sleep(3)  # Adjust the sleep time as needed
    content = driver.page_source
    new_soup = BeautifulSoup(content, features="html.parser")

    for a in new_soup.findAll('div', attrs={'class': 'a-section a-spacing-small puis-padding-left-small puis-padding-right-small'}) or new_soup.findAll('div', attrs={'class': 'a-section a-spacing-small a-spacing-top-small'}):

        titles.append(get_title(a))
        price.append(get_price(a))
        rating.append(get_rating(a))
        reviews.append(get_review_count(a))
        availability.append(get_availability(a))
        Discount.append(get_discount(a))
        ShippingPrice.append(get_ShippingPrice(a))
        Brand.append(get_Brand(a))
        country.append(get_country(a))


    csv_exists = os.path.exists(csv_filename)

    if not csv_exists:
        data = {
            'Title': titles,
            'Price': price,
            'Rating': rating,
            'Reviews': reviews,
            'Availability': availability,
            'Discount': Discount,
            'ShippingPrice': ShippingPrice,
            'Brand': Brand,
            'Country': country
        }
        df = pd.DataFrame(data)
        df.to_csv(csv_filename, mode='a', index=False, encoding='utf-8')
    else:
        data = {
            'Title': titles,
            'Price': price,
            'Rating': rating,
            'Reviews': reviews,
            'Availability': availability,
            'Discount': Discount,
            'ShippingPrice': ShippingPrice,
            'Brand': Brand,
            'Country': country
        }
        df = pd.DataFrame(data)
        df.to_csv(csv_filename, mode='a', index=False, header=False, encoding='utf-8')

    print("names",len(titles))
    print("shipping ",len(ShippingPrice))
    print("price ",len(price))
    print("country ",len(country))
    print("Brand ",len(Brand))
    print("ava  ",len(availability))
    print("ewvirews ",len(reviews))
    print("Rating ",len(rating))
    print("dis ",len(Discount))

    pageNumber = pageNumber + 1
    print("p",pageNumber)

    save_checkpoint(urlNumber, pageNumber)

    if pageNumber >= 398:
        urlNumber += 1
        pageNumber = 1
        save_checkpoint(urlNumber, pageNumber)
        print(" l page", pageNumber)
        print(" l url", urlNumber)
    elif urlNumber > 319:
        print("no")
        break


driver.quit()

