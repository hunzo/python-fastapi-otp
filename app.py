from fastapi import FastAPI
from datetime import timedelta

import os
from pydantic import BaseModel
import redis
import random
import string
import uuid

EXPIRES_MINUTES = os.environ.get("EXPIRES_MINUTES", 1)
REDIS_SERVER = os.environ.get("REDIS_SERVER", "localhost")


def connect():
    redisConnect = redis.Redis(host=REDIS_SERVER, port=6379)
    return redisConnect


r = connect()


def generate_otp():
    length = 6
    # return ''.join(random.choices(string.ascii_uppercase+string.digits, k=length))
    return ''.join(random.choices(string.digits, k=length))


def exist_key(key):
    if r.exists(key) == 1:
        exits = True
    else:
        exits = False
    return exits


def delete(key):
    success = False
    if exist_key(key):
        r.delete(key)
        success = True
    return success


app = FastAPI()


@app.post("/create_custom/{uuid_key}/{expired_minutes}")
def create_otp_customkey(uuid_key, expires_minutes):
    if exist_key(uuid_key):
        return "key already exits"

    otp = generate_otp()
    try:
        r.setex(uuid_key, timedelta(minutes=int(expires_minutes)), str(otp))
    except Exception as e:
        return e
    return {
        "otp": otp
    }


@app.post("/create")
def create_otp():
    key = uuid.uuid4()
    uuid_key = str(key)
    print(uuid_key)
    if exist_key(uuid_key):
        return "key already exits"

    otp = generate_otp()
    r.setex(uuid_key, timedelta(minutes=int(EXPIRES_MINUTES)), str(otp))

    return {
        "key": uuid_key,
        "otp": otp
    }


@app.delete("/delete/{uuid_key}")
def delete(uuid_key):
    success = False
    if exist_key(uuid_key):
        r.delete(uuid_key)
        success = True

    return success


@app.post("/auth/{uuid_key}/{otp}")
def authen(uuid_key: str, otp: str):
    success = False
    if exist_key(uuid_key):
        chk = r.get(uuid_key)
        otp = bytes(otp, 'utf-8')
        if chk == otp:
            delete(uuid_key)
            success = True
    return success
