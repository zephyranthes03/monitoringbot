import asyncio
import redis.asyncio as aioredis
import json
import os
import ast

from datetime import datetime, timedelta
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

        username = "root"
        username = os.getenv("MONGO_INITDB_ROOT_USERNAME","root")
        password = os.getenv("MONGO_INITDB_ROOT_PASSWORD","example")
        print(password, flush=True)
        mongo_host = "mongodb"  # hostname (can be localhost or a container name)
        mongo_port = 27017
        database_name = "database_scheduler"
        collection_name = "collection_scheduler"

        mongo_uri = f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/?authSource=admin"

        try:
            self.mongo_client = AsyncIOMotorClient(mongo_uri)
            self.db = self.mongo_client[database_name]

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
        finally:
            if self.redis_client is None:
                print("Redis 클라이언트가 None으로 설정되었습니다.")

    @property
    def get_db(self):
        return self.db

    @property
    def get_collection(self):
        return self.mongo_client['database_scheduler']['collection_scheduler'] 

    @property
    def get_redis(self):
        return self.redis_client


    async def inintialzie_service_data(self):
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection is None or self.get_redis is None:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis

        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            results = collection.find()
            async for result in results:
                service_info_text = await redis_client.get(result['chat_id'])
                service_info_json = dict()
                if service_info_text:
                    service_info_json = json.loads(service_info_text)                
                service_info_key = f"{result['host']}:{result['port']}"
                date_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                service_info_json[service_info_key] = {"chat_id": result['chat_id'], 
                                                        "host":result['host'], 
                                                        "port":result['port'],
                                                        "alias":result['alias'],
                                                        "time":date_string, 
                                                        "status":'init', 
                                                        "last_check_time":date_string
                                                    }
                service_info_text =json.dumps(service_info_json)
                await redis_client.set(result['chat_id'], service_info_text)


        # # Example operation: Fetch and print all documents from MongoDB collection
        # if collection:
        #     print("Documents in MongoDB collection:")
        #     async for document in collection.find():
        #         print(document)

        # # Example operation: Get and print a value from Redis
        # if redis_client:
        #     value = await redis_client.get('sample_key')
        #     print(f"Value for 'sample_key' in Redis: {value}")

    async def insert_service_data(self, chat_id:str, service_info:ServiceModel):
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection and self.get_redis:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis

        date_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + timedelta(seconds=service_info.time)
        lastcheck_date_string = service_data_model_info.last_check_time.strftime("%Y-%m-%d %H:%M:%S")
        service_flag = None
        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            filter = {'chat_id':chat_id, 'host': service_info.host, 'port':service_info.port}
            value = {'chat_id':chat_id, 'host': service_info.host, 'port':service_info.port, 'time':service_info.time, 'alias':service_info.alias }

            service_flag = await collection.replace_one(filter, value, upsert=True)
            print("Sample document inserted into MongoDB.")

        # Example operation: Set a value in Redis
        if redis_client is not None:
            service_info_key = f"{service_info.host}:{service_info.port}"
            service_data_model_info = ServiceDataModel(chat_id=chat_id,
                                                    host=service_info.host, 
                                                    port=service_info.port, 
                                                    alias=service_info.alias, 
                                                    )
            service_info_text = await redis_client.get(chat_id)
            service_info_json = dict()
            if service_info_text:
                service_info_json = json.loads(service_info_text)
            service_info_json[service_info_key] = {"host":service_info.host, 
                                                    "port":service_info.port,
                                                    "alias":service_info.alias,
                                                    "time":lastcheck_date_string, 
                                                    "status":'init', 
                                                    "last_check_time":lastcheck_date_string
                                                  }
            service_info_text =json.dumps(service_info_json)
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

        if self.get_collection and self.get_redis:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis


        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            await collection.delete_one({'chat_id': chat_id, 'host': service_info.host, 
                                        'port':service_info.port})
            print("Sample document delete into MongoDB.")

        # Example operation: Set a value in Redis
        if redis_client is not None:
            add_service_info = service_info.dict()
            service_info_key = f"{service_info.host}:{service_info.port}"
            service_info_text = await redis_client.get(chat_id)
            service_info_json = json.loads(service_info_text)
            del service_info_json[service_info_key]
            service_info_text = json.dumps(service_info_json)
            await redis_client.set(chat_id, service_info_text)
            print("Sample key-value pair set in Redis.")



    async def get_service_data(self, chat_id:str) -> dict:
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection and self.get_redis:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis

        # Example operation: Set a value in Redis
        if redis_client is not None:
            service_info_text = await redis_client.get(chat_id)
            print(type(service_info_text),flush=True)
            service_info_json = json.loads(service_info_text)
            if service_info_json:
                return service_info_json

        # Example operation: Insert a sample document into MongoDB
        elif collection is not None:
            result = await collection.find_one({'chat_id': chat_id})
            if result:
                return result


    async def get_services_by_chat_id(self, chat_id:str) -> dict:
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection and self.get_redis:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        redis_client = self.get_redis

        # Example operation: Set a value in Redis
        if redis_client is not None:
            service_info_text = await redis_client.get(chat_id)
            if service_info_text:
                print(service_info_text, flush=True)
                print(type(service_info_text), flush=True)
                service_info_json = json.loads(service_info_text)
                return service_info_json
            else:
                return None

        # Example operation: Insert a sample document into MongoDB
        elif collection is not None:
            result = await collection.find_one({'chat_id': chat_id})
            if result:
                return result


