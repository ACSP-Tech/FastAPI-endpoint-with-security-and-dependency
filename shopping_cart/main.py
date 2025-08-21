#importing the necessary requirements
from fastapi import FastAPI, HTTPException, status, Depends
from sec import SECRET_KEY, ALGORITHM
from .auth import check_filepath, check_user, require_admin, get_next_product_id, auth, CartFilepath, UserRegistration, UserRegOut, Userlogin, PromoteUserToAdmin, Product, CartIn
import json
import os
import jwt


#calling a fastapi instance
app = FastAPI()

@app.post("/register", response_model=UserRegOut, status_code=status.HTTP_201_CREATED)
def registration(detail:UserRegistration):
    try:
        check_user()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "user.json")
        #reading and loading json file
        with open(file_path, "r") as file:
            old_json = json.load(file)
        #automatic admin seeding logic
        role = "admin" if not old_json else "customer"
        #logic to check if email already exist in db case insensitive
        if detail.username.lower().strip() in old_json or any(
            detail.email.lower().strip() == users["email"]
            for users in old_json.values()
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="account with that email or and username already exit")
        else:
            if detail.username not in old_json:
                user_out = UserRegOut(
                    email = detail.email.lower().strip(),
                    role =  role
                )
                old_json[detail.username.lower().strip()] = user_out.model_dump()
                with open(file_path, "w") as file:
                    json.dump(old_json, file)
                return user_out
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with that email already exists")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/login", status_code=status.HTTP_200_OK)
def login(detail:Userlogin):
    try:
        check_user()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "user.json")
        #reading and loading the all current records
        with open(file_path, "r") as file:
            old_json = json.load(file)
        if detail.username.lower().strip() not in old_json:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="account with that email does not exit, Kindly login instead")
        elif detail.username.lower().strip() in old_json:
            payload = {
            "name": detail.username.lower().strip()
            }
            token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

            return {"token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/admin/promote_user", status_code=status.HTTP_200_OK)
def promote_user(data:PromoteUserToAdmin, admin=Depends(require_admin)):
    try:
        check_user()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "user.json")
        with open(file_path, "r") as file:
            users = json.load(file)
        if data.username not in users:
            raise HTTPException(status_code=404, detail="User not found")
        # Promote to admin
        users[data.username]["role"] = "admin"
        with open(file_path, "w") as file:
            json.dump(users, file)
        return {"message": f"User {data.username} promoted to admin successfully", "username": data.username, **users[data.username]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")



@app.post("/admin/add_product/", status_code=status.HTTP_201_CREATED)
def add_product(data:Product, admin=Depends(require_admin), id=Depends(get_next_product_id)):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "product.json")
        with open(file_path, "r") as file:
            product = json.load(file)
        check_user()
        if data.product_name.lower().strip() in product:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="product already exist")
        # add product if the name does not yet exist
        product[data.product_name.lower().strip()] = {
            "id": id,
            "selling_price": data.selling_price
        }
        with open(file_path, "w") as file:
            json.dump(product, file)
        return {"product_name": data.product_name.lower().strip(), **product[data.product_name.lower().strip()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/", status_code=status.HTTP_200_OK)
def view_product():
    try:
        check_filepath()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "product.json")
        with open(file_path, "r") as file:
            product = json.load(file)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/cart/add/", status_code=status.HTTP_201_CREATED)
def add_to_cart(data:CartIn, token=Depends(auth)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("name")
        
        #os module handling file path sourcing
        check_user()
        check_filepath()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "product.json")
        #reading and loading json file
        with open(file_path, "r") as file:
            old_json = json.load(file)
        #looping through till a match between parameter id and query id is found
        if data.product_name.lower().strip() in old_json and any(
            data.id == product["id"]
            for product in old_json.values()):
            CartFilepath()
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            file_path1 = os.path.join(BASE_DIR, "cart.json")
            #reading and loading json file
            with open(file_path1, "r") as file:
                cart_db = json.load(file)
            if username not in cart_db:
                cart_db[username] = []
            new_cart_item = {
                "id": data.id,
                "product_name": data.product_name,
                "selling_price": data.selling_price,
                "quantity": data.quantity,
                "total": round(data.quantity * data.selling_price, 2)
            }
            cart_db[username].append(new_cart_item)
            with open(file_path1, "w") as file:
                json.dump(cart_db, file)
            #return the current selection
            return cart_db[username]
        #if no match is found raise exception
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Product with id {data.id} and {data.product_name} not found") 
    except Exception as e:
        # Catches all other unexpected errors and shows them
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {e}")