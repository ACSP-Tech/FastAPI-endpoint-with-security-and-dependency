#importing the necessary requirement
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sec import SECRET_KEY, ALGORITHM
from pydantic import BaseModel, EmailStr
from typing import List
import json
import os
import jwt

auth = OAuth2PasswordBearer(tokenUrl="login") # http://127.0.0.1:8000/login

class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserRegOut(BaseModel):
    email: EmailStr
    role: str 

class Userlogin(BaseModel):
    username: str
    password: str

class PromoteUserToAdmin(BaseModel):
    username: str

class Product(BaseModel):
    product_name: str
    selling_price: float

class CartIn(BaseModel):
    id: int
    product_name: str
    selling_price: float
    quantity: int


#function to handling filepath exceptions and creation if necessary
def check_filepath():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        import json
        file_path1 = os.path.join(BASE_DIR, "product.json")
        if not os.path.exists(file_path1):
            with open(file_path1, "x") as file:
                json.dump({}, file)
    except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Error Creating Json file")
    
#function to handling filepath exceptions and creation if necessary
def check_user():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        import json
        file_path1 = os.path.join(BASE_DIR, "user.json")
        if not os.path.exists(file_path1):
            with open(file_path1, "x") as file:
                json.dump({}, file)
    except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Error Creating Json file")
    
def CartFilepath():
    #os module handling file path sourcing
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        import json
        file_path1 = os.path.join(BASE_DIR, "cart.json")
        #logic to trigger if file path does not exist, inessence, create an empty list
        if not os.path.exists(file_path1):
            with open(file_path1, "x") as file:
                json.dump({}, file)
    except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Error Creating Json file")


def get_current_user(token=Depends(auth)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("name")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "user.json")
        #reading and loading the all current records
        with open(file_path, "r") as file:
            old_json = json.load(file)
        if username.lower().strip() not in old_json:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="account with that email does not exit, Kindly login instead")
        return {"username": username, **old_json[username]}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    
def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user


def get_next_product_id() -> int:
    check_filepath()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "product.json")
    with open(file_path, "r") as file:
        products = json.load(file)
    if not products:  # if file is empty list
        return 1
    return max(product["id"] for product in products.values()) + 1

    
        