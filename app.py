from flask import Flask, render_template, request
from pymongo import MongoClient
import logging
# for special syntax and characters
import ast
import re  

# Initialization of flask application
task0 = Flask(__name__)

# Configuring log
logging.basicConfig(level=logging.DEBUG)

# Connecting MongoDB
client = MongoClient("mongodb+srv://ebayData:Fast2021@cluster0.kl8fsce.mongodb.net/")
db = client['Ebay_ScrappedData']
collection = db['Ebay-data']

# Function to handle missing/null values and remove $ char
def handle_chars(products):
    for product in products:
        try:
            if 'Price' in product and product['Price']:
                product['Price'] = float(product['Price'].replace('$', ''))
            else:
                product['Price'] = 0.0
            if 'Author' in product and (not product['Author'] or product['Author'] == 'NaN'):
                product['Author'] = 'Unknown'
            if 'Top-Rated Seller' in product and not product['Top-Rated Seller']:
                product['Top-Rated Seller'] = 'No'
            if 'Reviews' in product and isinstance(product['Reviews'], str):
                try:
                    # Convert the Reviews string back to a list of strings
                    # Handle syntax [' '] of reviews
                    product['Reviews'] = ast.literal_eval(product['Reviews'])
                except (ValueError, SyntaxError):
                    product['Reviews'] = ['No reviews']
            else:
                product['Reviews'] = ['No reviews']
            if 'Rating' in product and (not product['Rating'] or product['Rating'] == 'NaN'):
                product['Rating'] = 'N/A'
        except Exception as e:
            logging.error("Error normalizing product: %s, error: %s", product, e, exc_info=True)

# route definition
@task0.route('/')

# Function to retrieve  products and handle values
def index():
    try:
        # Retrieve all products from MongoDB
        products = list(collection.find())
        logging.debug("Products retrieved: %s", products)  # Debugging: Log retrieved products
        handle_chars(products)  # Handle before rendering
        return render_template('index.html', products=products)
    except Exception as e:
        logging.error("Error retrieving products: %s", e, exc_info=True)
        return "Error retrieving products from database."

# Search route definition
@task0.route('/search', methods=['GET'])

# Function to search products
def search():
    query = request.args.get('query')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    search_filter = {}

    # Search by title or auther
    if query:
        # Handling special characters for accurate search
        escaped_query = re.escape(query)
        search_filter['$or'] = [
            {'Title': {'$regex': escaped_query, '$options': 'i'}},
            {'Author': {'$regex': escaped_query, '$options': 'i'}}
        ]

    # Search by price range
    if min_price:
        min_price = float(min_price.replace('$', '')) if min_price else 0.0
        if 'Price' not in search_filter:
            search_filter['Price'] = {}
        search_filter['Price']['$gte'] = min_price

    if max_price:
        max_price = float(max_price.replace('$', '')) if max_price else float('inf')
        if 'Price' not in search_filter:
            search_filter['Price'] = {}
        search_filter['Price']['$lte'] = max_price

    # Handling and removing price key if needed
    if 'Price' in search_filter and not search_filter['Price']:
        del search_filter['Price']

    try:
        # Find products according to search filter
        products = list(collection.find(search_filter))
        logging.debug("Search filter: %s", search_filter)  # Debugging: Log search filter
        logging.debug("Products found: %s", products)  # Debugging: Log found products
        handle_chars(products)  # Handle values
        return render_template('index.html', products=products)
    except Exception as e:
        logging.error("Error searching products: %s", e, exc_info=True)
        return "Error searching products in database."

if __name__ == '__main__':
    task0.run(debug=True)

