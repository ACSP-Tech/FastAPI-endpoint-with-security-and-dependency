#importing the necessary requirements
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sec import SECRET_KEY, ALGORITHM, pwd_context
from .dep import check_filepath, check_students, auth
from typing import List

import json
import os
import jwt


#calling a fastapi instance
app = FastAPI(dependencies=[Depends(check_students)])

class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserRegOut(BaseModel):
    email: EmailStr
    username: str
    status: str 

@app.post("/register", response_model=UserRegOut, status_code=status.HTTP_201_CREATED)
def registration(detail:UserRegistration):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "student.json")
        #reading and loading json file
        with open(file_path, "r") as file:
            old_json = json.load(file)
        # hash password
        hashed_password = pwd_context.hash(detail.password)
        #logic to check if email already exist in db case insensitive
        if detail.username.lower().strip() in old_json or any(
            detail.email.lower().strip() == users["email"]
            for users in old_json.values()
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="account with that email or and username already exit")
        else:
            if detail.username not in old_json:
                user_out = UserRegOut(
                username= detail.username.lower().strip(),
                email = detail.email.lower().strip(),
                status = "success"
            )
                old_json[detail.username.lower().strip()] = {
                    "email": detail.email.lower().strip(),
                    "password": hashed_password
                }
                with open(file_path, "w") as file:
                    json.dump(old_json, file)
                return user_out
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with that email already exists")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

class Userlogin(BaseModel):
    username: str
    password: str

@app.post("/login", status_code=status.HTTP_200_OK)
def login(detail:Userlogin):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "student.json")
        #reading and loading the all current records
        with open(file_path, "r") as file:
            old_json = json.load(file)
        if detail.username.lower().strip() not in old_json:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="account with that email does not exit, Kindly login instead")
        elif detail.username.lower().strip() in old_json:
            username_key = detail.username.lower().strip()
            user = old_json[username_key]
            hashed = user.get("password")
            if not hashed or not pwd_context.verify(detail.password, hashed):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid username or password")
            payload = {
            "name": detail.username.lower().strip()
            }
            token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

            return {"token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

class Grade(BaseModel):
    name: str
    subject: str
    subject_scores: float
    average: float
    grade: str


class Student(BaseModel):
    username: str
    grades: List[Grade]

@app.get("/grades", status_code=status.HTTP_200_OK)
def auth_func(token=Depends(auth)):
    try:
        check_filepath()
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "student_result.json")
        #reading and loading the all current records
        with open(file_path, "r") as file:
            old_json = json.load(file)
        student_record = [student for student in old_json if student["name"].lower().strip() == payload["name"]]
        #if email already exist in db, do all the above
        db = Student(
            username = payload["name"],
            grades = student_record
        )
        return db
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



