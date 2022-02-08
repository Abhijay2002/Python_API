from typing import Optional, List
from os import stat
import string
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models,schemas, utils
from .database import engine, get_db
from .routers import post,user,auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:

    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='abhijay',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("successful")
        break
    except Exception as error:
        print("Failed to connect to db. Error:",error)
        time.sleep(2)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)