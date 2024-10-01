import asyncio
import redis.asyncio as aioredis
import json

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient  # Asynchronous MongoDB client
from model.service_model import ServiceModel, ServiceDataModel

class Database:
    """Singleton class to manage MongoDB and Redis connections asynchronously."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.mongo_client = None
            cls._instance.redis_client = None
        return cls._instance

    async def initialize_connections(self):
        """Initialize MongoDB and Redis connections asynchronously."""
        # MongoDB connection
        try:
            self.mongo_client = AsyncIOMotorClient('mongodb://mongodb:27017/')
            self.db = self.mongo_client['database_scheduler']
            collection_name = 'collection_scheduler'

            # Check if the collection exists; if not, create it
            existing_collections = await self.db.list_collection_names()
            if collection_name not in existing_collections:
                self.collection = self.db.create_collection(collection_name)
                print(f"Collection '{collection_name}' created.")
            else:
                self.collection = self.db[collection_name]
                print(f"Collection '{collection_name}' already exists.")

        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

        # Redis connection
        try:
            self.redis_client = await aioredis.from_url(
                'redis://redis:6379', encoding='utf-8', decode_responses=True
            )
            # Test the connection
            await self.redis_client.ping()
            print("Connected to Redis.")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")

    @property
    def get_db(self):
        return self.db

    @property
    def get_collection(self):
        return self.mongo_client['database_scheduler']['collection_scheduler'] 

    @property
    def get_redis(self):
        return self.redis_client


    async def insert_service_data(self, chat_id:str, service_info:ServiceModel):
        # Get the singleton instance of the AsyncDatabase class

        # Initialize connections asynchronously
        await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis

        service_flag = None
        # Example operation: Insert a sample document into MongoDB
        if collection:
            filter = {'chat_id':chat_id, 'host': service_info.host, 'port':service_info.port}
            value = {'chat_id':chat_id, 'host': service_info.host, 'port':service_info.port, 'time':service_info.time }

            service_flag = await collection.replace_one(filter, value, True)
            print("Sample document inserted into MongoDB.")

        # Example operation: Set a value in Redis
        if redis_client:
            service_info_key = f"{service_info.host}:{service_info.port}"
            service_data_model_info = ServiceDataModel(host=service_info.host, 
                                                    port=service_info.port, 
                                                    time=service_info.time, 
                                                    status='init', 
                                                    last_check_time=datetime.now() + timedelta(minutes=service_info.time)
                                                    )
            service_info_text = await redis_client.get(chat_id)
            service_info_json = json.loads(service_info_text)
            service_info_json[service_info_key] = service_data_model_info
            service_info_text = json.dumps(service_info_json)
            await redis_client.set(chat_id, service_info_text)
            print("Sample key-value pair set in Redis.")

        # # Example operation: Fetch and print all documents from MongoDB collection
        # if collection:
        #     print("Documents in MongoDB collection:")
        #     async for document in collection.find():
        #         print(document)

        # # Example operation: Get and print a value from Redis
        # if redis_client:
        #     value = await redis_client.get('sample_key')
        #     print(f"Value for 'sample_key' in Redis: {value}")


    async def remove_service_data(self, chat_id:str, service_info:ServiceModel):
        # Get the singleton instance of the AsyncDatabase class

        # Initialize connections asynchronously
        await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis


        # Example operation: Insert a sample document into MongoDB
        if collection:
            await collection.delete_one({'chat_id': chat_id, 'host': service_info.host, 
                                        'port':service_info.port})
            print("Sample document delete into MongoDB.")

        # Example operation: Set a value in Redis
        if redis_client:
            add_service_info = service_info.dict()
            service_info_key = f"{service_info.host}:{service_info.port}"
            service_info_text = await redis_client.get(chat_id)
            service_info_json = json.loads(service_info_text)
            del service_info_json[service_info_key]
            service_info_text = json.dumps(service_info_json)
            await redis_client.set(chat_id, service_info_text)
            print("Sample key-value pair set in Redis.")



    async def get_service_data(self, chat_id:str) -> dict():
        # Get the singleton instance of the AsyncDatabase class

        # Initialize connections asynchronously
        await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis

        # Example operation: Set a value in Redis
        if redis_client:
            service_info_text = await redis_client.get(chat_id)
            service_info_json = json.loads(service_info_text)
            if service_info_json:
                return service_info_json

        # Example operation: Insert a sample document into MongoDB
        if collection:
            result = await collection.find_one({'chat_id': chat_id})
            if result:
                return result
            print("Sample document delete into MongoDB.")


    async def get_serfvices_by_chat_id(self, chat_id:str) -> dict():
        # Get the singleton instance of the AsyncDatabase class

        # Initialize connections asynchronously
        await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis

        # Example operation: Set a value in Redis
        if redis_client:
            service_info_text = await redis_client.get(chat_id)
            service_info_json = json.loads(service_info_text)
            if service_info_json:
                return service_info_json

        # Example operation: Insert a sample document into MongoDB
        if collection:
            result = await collection.find_one({'chat_id': chat_id})
            if result:
                return result
            print("Sample document delete into MongoDB.")


