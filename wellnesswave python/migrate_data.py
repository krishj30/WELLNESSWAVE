from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('db.env')

def migrate_data():
    try:
        # Connect to both databases
        old_uri = "mongodb://localhost:27017/mental_health_db"
        new_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/krishdb')
        
        old_client = MongoClient(old_uri)
        new_client = MongoClient(new_uri)
        
        old_db = old_client["mental_health_db"]
        new_db = new_client["krishdb"]
        
        # Collections to migrate
        collections = ["users", "assessments"]
        
        for collection_name in collections:
            # Get data from old database
            old_collection = old_db[collection_name]
            new_collection = new_db[collection_name]
            
            # Clear the target collection first
            new_collection.delete_many({})
            print(f"✅ Cleared {collection_name} collection in target database")
            
            # Get all documents
            documents = list(old_collection.find())
            
            if documents:
                # Insert into new database
                new_collection.insert_many(documents)
                print(f"✅ Migrated {len(documents)} documents from {collection_name}")
            else:
                print(f"ℹ️ No documents found in {collection_name}")
        
        print("✅ Migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
    finally:
        # Close connections
        old_client.close()
        new_client.close()

if __name__ == "__main__":
    migrate_data() 