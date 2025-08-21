#importing the necessary requirement
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sec import SECRET_KEY, ALGORITHM

auth = OAuth2PasswordBearer(tokenUrl="login") # http://127.0.0.1:8000/login


#function to handling filepath exceptions and creation if necessary
def check_filepath():
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        import json
        file_path1 = os.path.join(BASE_DIR, "student_result.json")
        if not os.path.exists(file_path1):
            with open(file_path1, "x") as file:
                json.dump([], file)
    except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Error Creating Json file")
    
#function to handling filepath exceptions and creation if necessary
def check_students():
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        import json
        file_path1 = os.path.join(BASE_DIR, "student.json")
        if not os.path.exists(file_path1):
            with open(file_path1, "x") as file:
                json.dump({}, file)
    except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Error Creating Json file")

