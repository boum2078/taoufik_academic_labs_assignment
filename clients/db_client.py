from pymongo import MongoClient, ReplaceOne
import logging
import sys
from dotenv import load_dotenv
import json
import os 
load_dotenv(override=True)

class DBClient:
    def save_document(self, document):
        raise NotImplementedError("Subclasses should implement this method")

class MongoDBClient(DBClient):
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            handlers=[
                logging.FileHandler('clinical_trials_processing.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        url = os.getenv('MONGO_URI', "mongodb://mongo:27017")
        self.client = MongoClient(url)
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            self.logger.warning("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            self.logger.warning('Error connecting to MongoDB', str(e))
            raise e

        self.db = self.client["clinical_trials"]
        self.collection = self.db["studies"]

        self.logger.warning(f'Collections in my database are : {self.db.list_collection_names()}')
        self.logger.warning(f'Length of collection studies is : {(self.collection.count_documents({}))}')

        result = self.collection.create_index("trialId")
        self.logger.warning(f'Index created: {result}')

    def insert_many_documents(self, documents):
        ## to be check the update date before updating if many datasources
        operations = [
            ReplaceOne(
                {"trialId": doc["trialId"]},
                doc,
                upsert=True
            ) for doc in documents
        ]
        
        # Execute the bulk write operation
        result = self.collection.bulk_write(operations, ordered=False)
        
        self.logger.warning(f"Inserted/Updated {result.upserted_count + result.modified_count} documents")
        self.logger.warning(f"Inserted {result.upserted_count} documents")
        self.logger.warning(f"Updated  {result.modified_count} documents")
        # we can also check updating a few fields from other data sources

    def find_document(self):
        document = self.collection.find_one()
        # Convert ObjectId to string representation
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        document = json.dumps([document], indent=2)
        self.logger.warning(f'{document}')

class DBClientFactory:
    @staticmethod
    def get_db_client(db_type):
        if db_type == "mongo":
            return MongoDBClient()
        raise ValueError(f"Unknown database type: {db_type}")


if __name__ == "__main__":
    db_client = MongoDBClient()
    # db_client.find_document()