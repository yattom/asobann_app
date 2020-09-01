import random
import json
from pathlib import Path
from pymongo import operations
import pymongo.database

kits: pymongo.database.Database = None


def get(name):
    data = kits.find_one({"kit.name": name})
    if not data:
        return None
    del data['_id']
    return data


def get_all():
    data = kits.find()
    return [{"kit": d["kit"]} for d in data]


def connect(mongo):
    global kits
    kits = mongo.db.kits


def create(kit_data):
    assert 'kit' in kit_data
    assert 'name' in kit_data['kit']
    kits.insert_one({'kit': kit_data["kit"], 'version': 1})


def store_default(data):
    assert type(data) == list
    assert all(['kit' in d for d in data])
    assert all(['name' in d['kit'] for d in data])
    kits.bulk_write(
        [operations.UpdateOne({"kit.name": c["kit"]["name"]}, {"$set": c}, upsert=True) for c in data])


def purge_all():
    kits.delete_many({})
