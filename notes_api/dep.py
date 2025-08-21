#importing the necessary requirement
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
import json
import os
from datetime import date

auth = OAuth2PasswordBearer(tokenUrl="login")

class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserRegOut(BaseModel):
    email: EmailStr

class Userlogin(BaseModel):
    username: str
    password: str

class Note(BaseModel):
    title: str
    content: str

class NoteOut(BaseModel):
    title: str
    content: str
    date: date

#function to handling filepath exceptions and creation if necessary
def check_filepath():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        file_path1 = os.path.join(BASE_DIR, "notes.json")
        if not os.path.exists(file_path1):
            with open(file_path1, "x") as file:
                json.dump({}, file)
    except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Error Creating Json file")
    
#function to handling filepath exceptions and creation if necessary
def check_user():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        file_path1 = os.path.join(BASE_DIR, "user.json")
        if not os.path.exists(file_path1):
            with open(file_path1, "x") as file:
                json.dump({}, file)
    except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Error Creating Json file")

