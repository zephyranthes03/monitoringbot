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
            # cls._instance.redis_client = None
        return cls._instance

    async def initialize_connections(self):
        """Initialize MongoDB and Redis connections asynchronously."""
        # MongoDB connection

        username = "root"
        username = os.getenv("MONGO_INITDB_ROOT_USERNAME","root")
        password = os.getenv("MONGO_INITDB_ROOT_PASSWORD","example")
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
                # print(f"Collection '{collection_name}' already exists.")

        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

        # # Redis connection
        # try:
        #     self.redis_client = await aioredis.from_url(
        #         'redis://redis:6379', encoding='utf-8', decode_responses=True
        #     )
        #     # Test the connection
        #     await self.redis_client.ping()
        #     print("Connected to Redis.")
        # except Exception as e:
        #     print(f"Error connecting to Redis: {e}")
        # finally:
        #     if self.redis_client is None:
        #         print("Redis 클라이언트가 None으로 설정되었습니다.")

    @property
    def get_db(self):
        return self.db

    @property
    def get_collection(self):
        return self.mongo_client['database_scheduler']['collection_scheduler'] 

    # @property
    # def get_redis(self):
    #     return self.redis_client


    async def inintialzie_service_data(self):
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection is None:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        # redis_client = self.get_redis

        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            results = collection.find()
            async for result in results:
                service_info_json = dict()

    async def insert_service_data(self, chat_id:int, service_info:ServiceDataModel):
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection is None:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        # redis_client = self.get_redis

        datetime_now = datetime.now() 
        datetime_add_timedelta = datetime_now + timedelta(seconds=service_info.interval)
        
        service_flag = None
        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            filter = {'chat_id':chat_id, 'host': service_info.host, 'port':service_info.port}
            value = {'chat_id':chat_id, 'host': service_info.host, 'port':service_info.port, 
                     'last_check_time': datetime_now.isoformat(),
                     'next_check_time': datetime_add_timedelta.isoformat(),
                     'interval':service_info.interval, 'alias':service_info.alias }

            service_flag = await collection.replace_one(filter, value, upsert=True)
            print("Sample document inserted into MongoDB.")

        # # Example operation: Set a value in Redis
        # if redis_client is not None:
        #     service_info_key = f"{service_info.host}:{service_info.port}"
        #     service_data_model_info = ServiceDataModel(chat_id=chat_id,
        #                                             host=service_info.host, 
        #                                             port=service_info.port, 
        #                                             alias=service_info.alias, 
        #                                             )
        #     service_info_text = await redis_client.get(chat_id)
        #     service_info_json = dict()
        #     if service_info_text:
        #         service_info_json = json.loads(service_info_text)
        #     service_info_json[service_info_key] = {"host":service_info.host, 
        #                                             "port":service_info.port,
        #                                             "alias":service_info.alias,
        #                                             "time":datetime_now_str, 
        #                                             "status":'init', 
        #                                             "last_check_time":datetime_add_timedelta_str,
        #                                             "interval": service_info.interval
        #                                           }
        #     service_info_text =json.dumps(service_info_json)
        #     await redis_client.set(chat_id, service_info_text)
            # print("Sample key-value pair set in Redis.")



    async def update_service_data(self, chat_id:int, service_info:ServiceDataModel):
        # Get the singleton instance of the AsyncDatabase class
        print(chat_id, flush=True)
        print(type(chat_id), flush=True)
        if self.get_collection is None:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        # redis_client = self.get_redis
        
        service_flag = None
        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            filter = {'chat_id':chat_id, 'host': service_info.host, 'port':service_info.port}
            
            service_info.chat_id = chat_id
            print(service_info, flush=True)
            print(service_info.model_dump(), flush=True)

            service_flag = await collection.replace_one(filter, service_info.model_dump(), upsert=True)
            print("Sample document inserted into MongoDB.")

        # # Example operation: Set a value in Redis
        # if redis_client is not None:
        #     datetime_now_str = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
        #     datetime_add_timedelta_str = datetime_add_timedelta.strftime("%Y-%m-%d %H:%M:%S")
        #     service_info_key = f"{service_info.host}:{service_info.port}"
        #     service_data_model_info = ServiceDataModel(chat_id=chat_id,
        #                                             host=service_info.host, 
        #                                             port=service_info.port, 
        #                                             alias=service_info.alias, 
        #                                             )
        #     service_info_text = await redis_client.get(chat_id)
        #     service_info_json = dict()
        #     if service_info_text:
        #         service_info_json = json.loads(service_info_text)
        #     service_info_json[service_info_key] = {"host":service_info.host, 
        #                                             "port":service_info.port,
        #                                             "alias":service_info.alias,
        #                                             "time":datetime_now_str, 
        #                                             "status":'init', 
        #                                             "last_check_time":datetime_add_timedelta_str,
        #                                             "interval": service_info.interval
        #                                           }
        #     service_info_text =json.dumps(service_info_json)
        #     await redis_client.set(chat_id, service_info_text)
        #     print("Sample key-value pair set in Redis.")


    async def remove_service_data(self, chat_id:int, service_info:ServiceModel):
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection is None:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        # redis_client = self.get_redis


        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            if service_info.alias is None:
                await collection.delete_one({'chat_id': chat_id, 'host': service_info.host, 
                                            'port':service_info.port})
            else:
                await collection.delete_one({'chat_id': chat_id, 'alias': service_info.alias})
            print("Sample document delete into MongoDB.")


    # Update check Time routine 
    async def get_services_by_time(self, datetime_range:datetime) -> list:
        # Get the singleton instance of the AsyncDatabase class
        print(datetime_range.isoformat(),flush=True)
        return_result = list()
        if self.get_collection is None:
            # Initialize connections asynchronously
            await self.initialize_connections()

        # Use the shared MongoDB collection and Redis client
        collection = self.get_collection
        print(collection,flush=True)

        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            results = collection.find({'next_check_time':{'$lt': datetime_range}})
            # results = collection.find({})
            async for result in results:
                return_result.append(result)

        return return_result



    async def get_services_by_chat_id(self, chat_id:str) -> dict:
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection is None:
            # Initialize connections asynchronously
            await self.initialize_connections()

        collection = self.get_collection

        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            result = await collection.find_one({'chat_id': chat_id})
            return result
        else:
            return None



    async def get_service_by_chat_id_and_alias(self, chat_id:str, alias:str) -> dict:
        # Get the singleton instance of the AsyncDatabase class

        if self.get_collection is None:
            # Initialize connections asynchronously
            await self.initialize_connections()

        collection = self.get_collection

        # Example operation: Insert a sample document into MongoDB
        if collection is not None:
            result = await collection.find_one({'chat_id': chat_id, 'alias': alias})
            return result
        else:
            return None

