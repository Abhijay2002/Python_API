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


models.Base.metadata.create_all(bind=engine)

app = FastAPI()



class Post(BaseModel):
    title:str
    content:str
    published:bool = True
while True:

    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='abhijay',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("successful")
        break
    except Exception as error:
        print("Failed to connect to db. Error:",error)
        time.sleep(2)

@app.get("/")
async def root():
    return {"message": "First api_prg"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return{"status":"success"}

@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post:Post,db: Session = Depends(get_db)):
    #cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s, %s, %s) RETURNING * """,(post.title,post.content,post.published))
    #new_post = cursor.fetchone()
    #conn.commit()

    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post 


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts WHERE id = %s""",(str(id),))
    #post = cursor.fetchone()
    
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"post with id: {id} was not found")
    return post



@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""DELETE FROM posts WHERE id = %s returning *""",(str(id),))
    #deleted_post = cursor.fetchone()
    #conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"post with id: {id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, post: Post,db: Session = Depends(get_db)):

    #cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id= %s RETURNING *""", 
    #(post.title,post.content,post.published, str(id)))

    #updated_post = cursor.fetchone()
    #conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id== id)
    updated_post = post_query.first()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} does not exist")
    
    post_query.update(post.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate, db: Session = Depends(get_db)):

    # hashing the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

@app.get('/users/{id}')
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} does not exist")
    
    return user