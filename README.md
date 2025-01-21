# User Authentication Microservice

This project is a user authentication microservice built with **FastAPI** and **SQLite**, designed to provide secure user registration, login, and token-based authentication using JWT.

---

## **Features**
- User registration with hashed passwords.
- Secure login with JSON Web Tokens (JWT).
- SQLite as the database for lightweight and fast storage.
- Implements modern Python features (e.g., type hints, PEP-8 compliance).
- Dockerized for easy deployment.

---

## **Getting Started**

### **Prerequisites**
- [Python 3.11+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/)
- [Poetry](https://python-poetry.org/) for dependency management.

### **Installation**

#### **Without Docker**

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/user-auth-microservice.git
   cd user-auth-microservice

2. Install dependencies:
   ```bash
   poetry install

3. Create the .env file:
   ```bash
   cp .env.example .env
   
4. Initialize the database:
   ```bash
   python -m scripts.init_db

5. Run the development server:
   ```bash
   uvicorn api.main:app --reload
   
#### **With Docker**
1. Build and run the Docker containers:
   ```bash
   docker-compose up --build

2. The application will be available at http://localhost:8000.


## **API Endpoints**



| Method |         Endpoint          | Description                                       |
|:------:|:-------------------------:|:--------------------------------------------------|
|  POST  |   **v1/auth/register**    | Register a new user.                              |
|  POST  |     **v1/auth/login**     | Login and obtain a JWT token and a refresh token. |
|  POST  | **v1/auth/refresh-token** | Refresh token for a given token.                  |
|  POST  | **v1/auth/revoke-token**  | Blacklist a token manually.                       |
|  GET   | **v1/user/login-history** | Obtain the login history of an user.              |

#### **cURL's**
1. **v1/auth/register**
   ```bash
   curl --location '{{host}}/auth/register' \
    --request POST \
    --header 'Content-Type: application/json' \
    --data '{
        "username": {{username}},
        "password": {{password}}
    }'
   
2. **v1/auth/login**
   ```bash
   curl --location '{{host}}/auth/login' \
    --request POST \
    --header 'Content-Type: application/json' \
    --data '{
        "username": {{username}},
        "password": {{password}}
    }'
   
3. **v1/auth/refresh-token**
   ```bash
   curl --location --request POST '{{host}}/auth/refresh-token?token={{refresh_tokn}}
   

4. **v1/auth/revoke-token**
   ```bash
   curl --location --request POST '{{host}}/auth/revoke-token?token={{token}}'
   

5. **v1/user/login-history**
   ```bash
   curl --location '{{host}}/auth/login-history' \
    --request POST \
    --header 'Authorization: Bearer {{token}}'
   
#### **Swagger**

localhost:8000/docs#/