# Import required libraries
import pandas as pd
import pymongo
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Read the CSV file
df = pd.read_csv('/content/drive/My Drive/FatimaQurban_PCN_Internship/PCNInternship_FatimaQurban_Task0/ebay_psychology_books.csv')

# Convert DataFrame to a list of dictionaries
data = df.to_dict(orient='records')

# Get the MongoDB connection string from the environment variable
connection_string = os.getenv("MONGO_CONNECTION_STRING")

# Connect to MongoDB Atlas
client = pymongo.MongoClient(connection_string)

# Select the database
db = client["Ebay_ScrappedData"]

# Select the collection (creating it if it doesn't already exist)
collection = db["Ebay-data"]

# Insert the data
collection.insert_many(data)
print("Data inserted successfully!")
