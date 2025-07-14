from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, Post
from schemas import UserCreate, PostCreate, Post, Token
from auth import authenticate_user, create_token, get_current_user
from crud import create_user, create_post, get_posts, get_post
from fastapi.security import OAuth2PasswordRequestForm

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/signup", response_model=dict)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    create_user(db, user)
    return {"msg": "User created successfully"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/posts", response_model=Post)
def create_new_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_post(db, post, user_id=current_user.id)

@app.get("/posts", response_model=list[Post])
def list_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_posts(db, skip=skip, limit=limit)

@app.get("/posts/{post_id}", response_model=Post)
def get_single_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
