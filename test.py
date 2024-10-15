from pymongo import MongoClient

# Replace 'username', 'password', and 'your_cluster_url' with your actual credentials and cluster URL
username = 'Evil'
password = '123'
cluster_url = 'cluster0.n69njhi.mongodb.net'

# Create the connection URI
connection_uri = f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority"

# Connect to the MongoDB cluster
client = MongoClient(connection_uri)

# Replace 'your_database_name' with the actual name of your database
db = client['Viz']

# List all collections in the database
collections = list(db.list_collection_names())

print("Collections in the database:", collections)
