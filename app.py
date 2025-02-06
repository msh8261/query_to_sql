import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy import create_engine, text
import json
import uvicorn
from main import AgentSystem
from config import db_info
from log import logger
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
mysql_host = os.getenv("mysql_host", "localhost")
mysql_port = int(os.getenv("mysql_port", "3306"))
mysql_user = os.getenv("mysql_user", "root")
mysql_password = os.getenv("mysql_password", "")
mysql_database = os.getenv("mysql_database", "chatbot")

# Database URL
DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

# SQLAlchemy Engine & Session
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


async def get_sql(query: str):
    sql_system = AgentSystem(dataset_information=db_info, max_retry=3)
    try:
        responses = await sql_system.forward(query=query)
        logger.debug(f"sql generated: {responses}")
        return responses
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        raise


# Define the request model for receiving the query
class QueryRequest(BaseModel):
    query: str


@app.post("/execute_query/")
async def execute_query(request: QueryRequest):
    try:
        # Await the result of the asynchronous get_sql function
        result = await get_sql(request.query)  # Await here
        
        # The generated SQL is wrapped in a list, so we need to extract the query
        result_sql = str(result["sql"][0])  # Extract the first item from the list
        
        logger.debug(f"Executing query: {result_sql}")
        
        # Execute SQL query on the database
        with engine.connect() as conn:
            result = conn.execute(text(result_sql))
            logger.debug(f"Query result: {result}")
            
            # Fetch all rows from the result and convert them into a list of dictionaries
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            
            # Convert Decimal to float for easier handling in JavaScript
            for row in rows:
                row['total_sales_units'] = float(row['total_sales_units'])
            
            logger.debug(f"Rows: {rows}")
            return {"data": rows}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))






@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":  # Ensures the script runs when executed directly
    uvicorn.run(
        "app:app",  # Points to the FastAPI app object (assuming app.py defines the app as 'app')
        host="0.0.0.0",  # Makes the server accessible on all network interfaces (useful for Docker/production)
        port=8001,  # Sets the port number to 8001
        log_level="debug"  # Sets the log level to debug for more detailed logging
    )
