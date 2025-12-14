import os
import motor.motor_asyncio
import pymongo

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://mongodb:27017')

async_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
async_db = async_client.kandidate_db
async_job_collection = async_db.jobs

sync_client = pymongo.MongoClient(MONGO_URL)
sync_db = sync_client.kandidate_db
sync_job_collection = sync_db.jobs
