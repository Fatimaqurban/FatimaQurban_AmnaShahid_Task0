import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Function to extract product details from eBay
def scrape_ebay_products(search_query, num_pages=1):
    base_url = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313&_nkw=Psychology+Books&_sacat=0&_odkw=toy+car&_osacat=0"
    items = []

    for page in range(1, num_pages + 1):
        params = {
            "_nkw": search_query,
            "_ipg": 50,  # Items per page
            "_pgn": page
        }

        response = requests.get(base_url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.select('.s-item'):
            title = item.select_one('.s-item__title')
            price = item.select_one('.s-item__price')
            author = item.select_one('.s-item__subtitle')
            top_rated = item.select_one('.s-item__etrs-text')
            reviews_link = item.select_one('.s-item__reviews a')  # Link to reviews

            #handling reviews to go to the review url
            if reviews_link:
                product_url = reviews_link['href']
                reviews, rating = scrape_product_reviews(product_url)
            else:
                reviews, rating = None, None


            #handling wrong authors stored
            author_text = author.get_text(strip=True) if author else None
            if author_text and not author_text.startswith("by"):
                author_text = None


            item_data = {
                "Title": title.get_text(strip=True) if title else None,
                "Price": price.get_text(strip=True) if price else None,
                "Author": author_text,
                "Top-Rated Seller": 'Yes' if top_rated else 'No',
                "Reviews": reviews,
                "Rating": rating
            }
            items.append(item_data)

    return items

#Extracting review and ratings from thr href tag on the reviews
def scrape_product_reviews(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    reviews = []
    review_elements = soup.select('.review--content')
    for review_element in review_elements:
        review_text = review_element.get_text(strip=True)
        reviews.append(review_text)

    rating_element = soup.select_one('.review--star--rating .clipped')
    if rating_element:
        rating_text = rating_element.get_text(strip=True)
        rating = rating_text.split()[0] # get first element. E.g. for a comment like '4 out of 5 stars' it would pick 4 only
    else:
        rating = None

    return reviews, rating


# Main function to execute the scraping and save data to CSV
def main():
    search_query = "Psychology Book"
    num_pages = 3
    products = scrape_ebay_products(search_query, num_pages)

    # Save the scraped data to a CSV file
    df = pd.DataFrame(products)    #dataframes are best for handling and manipulating the data
    df = df.applymap(lambda x: x if x else pd.NA)
    df.to_csv('ebay_psychology_books.csv', index=False)
    print(f"Scraped {len(products)} items and saved to 'ebay_psychology_books.csv'")


    # Save the scraped data to a JSON file
    with open('ebay_psychology_books.json', 'w') as json_file:
      json.dump(products, json_file, indent=4)
    print(f"Scraped {len(products)} items and saved to 'ebay_psychology_books.json'")

if __name__ == "__main__":
    main()
