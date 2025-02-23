import csv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB connection
try:
    client = MongoClient("mongodb+srv://my-user:vVgi4WfgzYA7CJBr@cluster0.kbovzuj.mongodb.net/")
    # Test the connection
    client.admin.command('ping')
    print("Connected to the database successfully.")
except ConnectionFailure:
    print("Failed to connect to the database.")
    exit(1)  # Exit the script if the connection fails

db = client["db_adbms"]  # Use your database name
collection = db["netflix"]  # Specify the collection name

# Clear the collection before seeding
collection.delete_many({})
print("Cleared existing records in the collection.")

# Read the CSV file and insert data into MongoDB
with open('IMDB-Movie-Data.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    records = list(reader)  # Convert to a list to count records
    print(f"Found {len(records)} records in the CSV file.")

    for index, row in enumerate(records):
        # Convert numeric fields to appropriate types
        row['Year'] = int(row['Year'])
        row['Runtime'] = int(row['Runtime'])
        row['Rating'] = float(row['Rating']) if row['Rating'] else None
        row['Votes'] = int(row['Votes']) if row['Votes'] else None
        row['Revenue'] = float(row['Revenue']) if row['Revenue'] else None
        
        # Insert the row into the collection
        collection.insert_one(row)
        print(f"Inserted record {index + 1}/{len(records)}: {row['Title']}")

print("Data seeded successfully.") 