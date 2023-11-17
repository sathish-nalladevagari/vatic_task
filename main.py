from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import OAuth2PasswordBearer

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
# Use SessionMiddleware with a secret key for secure sessions
app.add_middleware(SessionMiddleware, secret_key="secret123")

# Create MySQL connection
connection = mysql.connector.connect(**mysql_config)
cursor = connection.cursor()

# OAuth2PasswordBearer for handling token authentication (not used in this example)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Jinja2 template configuration
templates = Jinja2Templates(directory="templates")

# Function to get the current user based on the provided token (not used in this example)
def get_current_user(token: str = Depends(oauth2_scheme)):
    return token

def is_admin(username: str = Depends(get_current_user)):
    # Replace the following logic with your actual database query
    select_role_query = "SELECT role FROM users WHERE username = %s"
    cursor.execute(select_role_query, (username,))
    role = cursor.fetchone()

    return role == 'admin' if role else False

# Home page with login form
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login endpoint
@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Check if the username and password match a user in the database
    select_user_query = "SELECT username, password, role FROM users WHERE username = %s"
    cursor.execute(select_user_query, (username,))
    user_data = cursor.fetchone()

    if user_data and user_data[1] == password:
        username = user_data[0]
        role = user_data[2]
        return templates.TemplateResponse("welcome.html", {"request": request, "username": username, "role": role})
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/show_users", response_class=HTMLResponse)
async def show_users(request: Request):
    # Establish a database connection
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor(dictionary=True)

    try:
        # Get all users from the database
        select_users_query = "SELECT id, username, email FROM users"
        cursor.execute(select_users_query)
        users = cursor.fetchall()

        return templates.TemplateResponse("show_users.html", {"request": request, "users": users})
    finally:
        # Close the database connection
        connection.close()
# Endpoint to handle the form submission
@app.post("/create_entity", response_class=HTMLResponse)
def create_entity(
    request: Request,
    entity_type: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
):
    # Check if the user is an admin
    # Implement your own logic to get the user's role based on the session or token
    role = "admin"  # For demonstration purposes, assuming the user is an admin

    if role != 'admin':
        raise HTTPException(status_code=403, detail="Access forbidden. You do not have permission to create entities.")

    # Perform the creation logic based on the selected entity type
    if entity_type == 'user':
        create_user_query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        user_data = (username, password, email)
        try:
            cursor.execute(create_user_query, user_data)
            connection.commit()
            message = "User created successfully!"
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            message = "Error creating user."

    elif entity_type == 'admin':
        create_admin_query = "INSERT INTO admins (username, password, email) VALUES (%s, %s, %s)"
        admin_data = (username, password, email)
        try:
            cursor.execute(create_admin_query, admin_data)
            connection.commit()
            message = "Admin created successfully!"
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            message = "Error creating admin."

    else:
        raise HTTPException(status_code=400, detail="Invalid entity type selected.")

    return templates.TemplateResponse(
        "welcome.html", {"request": request, "username": username, "role": role, "message": message}
    )
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
