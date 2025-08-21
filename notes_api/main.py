#importing the necessary requirements
from fastapi import FastAPI, HTTPException, status, Depends
from sec import SECRET_KEY, ALGORITHM
from .dep import check_filepath, check_user, auth, UserRegistration, UserRegOut, Userlogin, Note, NoteOut
from datetime import date
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="account with that email or username does not exist")
        elif detail.username.lower().strip() in old_json:
            payload = {
            "name": detail.username.lower().strip()
            }
            token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

            return {"token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/notes/", status_code=status.HTTP_201_CREATED, response_model=NoteOut)
def add_notes(data:Note, token=Depends(auth)):
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
        file_path1 = os.path.join(BASE_DIR, "notes.json")
        #reading and loading json file
        with open(file_path1, "r") as file:
            notes_db = json.load(file)
        if username not in notes_db: 
            notes_db[username] = []
        new_note = NoteOut(
            title = data.title.lower().strip(),
            content = data.content.lower().strip(),
            date = date.today()
        )
        if any(
            data.title.lower().strip() == note["title"]
            for note in notes_db.get(username, [])
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=" note title already exist for this user")
        notes_db[username].append(json.loads(new_note.model_dump_json()))
        with open(file_path1, "w") as file:
            json.dump(notes_db, file)
        #return the current selection
        return new_note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/notes/", status_code=status.HTTP_200_OK)
def view_note(token=Depends(auth)):
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
        file_path1 = os.path.join(BASE_DIR, "notes.json")
        #reading and loading json file
        with open(file_path1, "r") as file:
            note_db = json.load(file)
        if username not in note_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no notes record yet")
        #return the current selection
        return note_db[username]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))