#importing the necessary requirements
from fastapi import FastAPI, HTTPException, status, Depends
from sec import SECRET_KEY, ALGORITHM, pwd_context
from .dep import check_filepath, check_user, auth, UserRegistration, UserRegOut, Userlogin, JobApplications
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
        # hash password
        hashed_password = pwd_context.hash(detail.password)
        #logic to check if email and username already exist in db case insensitive
        if detail.username.lower().strip() in old_json or any(
            detail.email.lower().strip() == users["email"]
            for users in old_json.values()
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="account with that email or and username already exit")
        else:
            if detail.username not in old_json:
                user_out = UserRegOut(
                    email = detail.email.lower().strip(),
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


@app.post("/applications/", status_code=status.HTTP_201_CREATED)
def add_job_application(data:JobApplications, token=Depends(auth)):
    try:
        check_user()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("name")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "user.json")
        with open(file_path, "r") as file:
            users = json.load(file)
        if username not in users:
            raise HTTPException(status_code=404, detail="User not found")
        #logic to add new applications
        check_filepath()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path1 = os.path.join(BASE_DIR, "applications.json")
        #reading and loading json file
        with open(file_path1, "r") as file:
            job_db = json.load(file)
        if username not in job_db:
            job_db[username] = []
        # Normalize string fields, keep date intact
        normalized = {
            "job_title": data.job_title.lower().strip(),
            "company": data.company.lower().strip(),
            "date_applied": str(data.date_applied),   # keep as string in JSON
            "status": data.status.lower().strip()
        }
        if any(
        normalized == job for job in job_db.get(username, [])
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="a matching job with same info already exist for  this user")    
        job_db[username].append(normalized)
        with open(file_path1, "w") as file:
            json.dump(job_db, file)
        #return the current selection
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/applications/", status_code=status.HTTP_201_CREATED)
def view_job_application(token=Depends(auth)):
    try:
        check_user()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("name")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "user.json")
        with open(file_path, "r") as file:
            users = json.load(file)
        if username not in users:
            raise HTTPException(status_code=404, detail="User not found")
        #logic to add new applications
        check_filepath()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path1 = os.path.join(BASE_DIR, "applications.json")
        #reading and loading json file
        with open(file_path1, "r") as file:
            job_db = json.load(file)
        if username not in job_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no job record yet")
        #return the current selection
        return job_db[username]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))