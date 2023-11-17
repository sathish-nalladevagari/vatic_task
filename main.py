from fastapi import FastAPI, Form, Depends, HTTPException,Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mysql_config = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'password123',
    'database': 'users',
}

# Create MySQL connection
connection = mysql.connector.connect(**mysql_config)
cursor = connection.cursor()

# Fake user data for demonstration purposes (replace with a database)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "password": "testpassword",
    }
}

# OAuth2PasswordBearer for handling token authentication (not used in this example)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Jinja2 template configuration
templates = Jinja2Templates(directory="templates")

# Function to get the current user based on the provided token (not used in this example)
def get_current_user(token: str = Depends(oauth2_scheme)):
    return token

# Home page with login form
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login endpoint
@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Check if the username and password match a user in the fake database
    user = fake_users_db.get(username)
    if user and user["password"] == password:
        return templates.TemplateResponse("welcome.html", {"request": request, "username": username})
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Create user endpoint
@app.post("/create_user", response_class=HTMLResponse)
def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
):
    # Insert user into the MySQL database
    insert_user_query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
    user_data = (username, password, email)

    try:
        cursor.execute(insert_user_query, user_data)
        connection.commit()
        message = "User created successfully!"
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        message = "Error creating user."

    return templates.TemplateResponse(
        "welcome.html", {"request": request, "message": message}
    )

@app.get("/show_users", response_class=HTMLResponse)
def show_users(request: Request):
    # Retrieve all users from the MySQL database
    select_users_query = "SELECT username, email FROM users"
    
    cursor.execute(select_users_query)
    users = cursor.fetchall()

    return templates.TemplateResponse("show_users.html", {"request": request, "users": users})


    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
