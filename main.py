# main.py (FastAPI Backend)

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import sqlite3
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List

app = FastAPI()
SECRET_KEY = "YOUR_SECRET_KEY"  # CHANGE THIS!
ALGORITHM = "HS256"
DATABASE_FILE = "on_duty.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

# ... (Database functions, models, JWT functions - same as before, but include these changes)

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(credentials: HTTPBasicCredentials, db: sqlite3.Connection = Depends(get_db)):
    # ... (Login logic - same as before)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, token: dict = Depends(decode_access_token)):
    # ... (Check user role, fetch data, render appropriate dashboard)

@app.post("/on_duty_requests", status_code=status.HTTP_201_CREATED)
async def create_on_duty_request(request: Request, on_duty_request: OnDutyRequest, token: dict = Depends(decode_access_token), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
            
    return {"message": "On Duty request created successfully"}

@app.get("/on_duty_requests", response_model=List[OnDutyRequest]) # Use response_model
async def get_on_duty_requests(request: Request, token: dict = Depends(decode_access_token), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    if token["role"] == "admin":
      cursor.execute("SELECT * FROM on_duty_requests")
    else:
      cursor.execute("SELECT * FROM on_duty_requests WHERE user_id=?", (token["sub"],))
    requests = cursor.fetchall()
    # Convert to Pydantic objects
    on_duty_requests = []
    for req in requests:
      on_duty_requests.append(OnDutyRequest(start_date=req[2], end_date=req[3], reason=req[4]))
    return on_duty_requests

@app.put("/on_duty_requests/{request_id}")
async def update_on_duty_request(request: Request, request_id: int, status: str, token: dict = Depends(decode_access_token), db: sqlite3.Connection = Depends(get_db)):
    if token["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    cursor = db.cursor()
    cursor.execute("UPDATE on_duty_requests SET status=? WHERE id=?", (status, request_id))
    db.commit()
    return {"message": "On Duty request updated successfully"}

# ... (Other API endpoints)

# Database Initialization (Run this once):
def create_tables():
    # ... (Same table creation SQL as before)

    if __name__ == "__main__":
        # ... (Same as before)