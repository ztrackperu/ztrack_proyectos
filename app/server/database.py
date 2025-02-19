#import motor.motor_asyncio
from bson.objectid import ObjectId
from decouple import config
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

#MONGO_DETAILS = config("MONGO_DETAILS")  # read environment variable MONGODB_USERNAME MONGODB_URI
#mongodb://test_proyecto:test_proyecto_pass@localhost:27019/
#MONGO_DETAILS = "mongodb://"+config("MONGODB_USERNAME")+":"+config("MONGODB_PASSWORD")+"@"+config("MONGODB_URI")
GENIAL = f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_URI')}/{os.getenv('MONGODB_DB')}"

print("*************")
print(GENIAL)
print("*************")

#BD_DETAILS =config("BD_DETAILS")
#BD_DETAILS_A =config("MONGODB_DB")
#client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
#integrado es nombre para la base de datos
#database = client[BD_DETAILS]
#database = client[BD_DETAILS_A]

mongo_db_name=os.getenv('BD_DETAILS')
print("*************")
print(mongo_db_name)
print("*************")
#client = AsyncIOMotorClient(MONGO_URI)
client = AsyncIOMotorClient(GENIAL)
#mongo_db = client.get_database()
database_mongo = client[mongo_db_name] 
#database_mongo =client.mongo_db_name

async def collection(data):
    data_collection = database_mongo.get_collection(data)
    return data_collection
