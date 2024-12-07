from fastapi import FastAPI, Path, HTTPException, status, Body, Request, Form
from typing import Annotated, List
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True}, debug=True)
templates = Jinja2Templates(directory="templates")

users = []

class User(BaseModel):
    id: int
    username: str
    age: int

@app.get("/")
def get_all_users(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.get(path='/users/{user_id}')
def get_users(request: Request, user_id: int) -> HTMLResponse:
    for user in users:
        if user.id == user_id:
            return templates.TemplateResponse("users.html", {"request": request, "user": user})


@app.post('/user/{username}/{age}', status_code=status.HTTP_201_CREATED)
def post_user(request: Request, user: User,
                    username: Annotated[str, Path(min_length=5,
                                                  max_length=20,
                                                  description='Enter username')],
                    age: int = Path(ge=18,
                                    le=120,
                                    description="Enter age")) -> HTMLResponse:
    if users:
        user_id = max(users, key= lambda u: u.id).id + 1
    else:
        user_id = 0
    users.append(User(id=user_id, username=username, age=age))
    return templates.TemplateResponse("users.html", {"request": request, "User": users})


@app.put('/user/{user_id}/{username}/{age}', response_model=User)
async def update_user(user: User, user_id: int,
                      username: Annotated[str, Path(min_length=5,
                                                    max_length=20,
                                                    description='Enter username')],
                      age: int = Path(ge=18,
                                      le=120,
                                      description="Enter age")):
    for u in users:
        if u.id == user_id:
            u.username = username
            u.age = age
            return u
    raise HTTPException(status_code=404, detail="User was not found")


@app.delete('/user/{user_id}')
async def delete_user(user_id: int):
     for i, u in enumerate(users):
         if u.id == user_id:
             users.pop(i)
             return {f'User {user_id} is delete'}
     raise HTTPException(404, 'User was not found')

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
