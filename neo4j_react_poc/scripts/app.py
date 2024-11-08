import os
import json
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from langchain_community.graphs import Neo4jGraph

# Load environment variables from .env file
load_dotenv()

# Now use environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")  

# Initialize the Neo4j graph and refresh schema
graph = Neo4jGraph()
graph.refresh_schema()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed for your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Load queries from a JSON file
#with open('queries.json') as f:
#    queries = json.load(f)

# Request model
class QueryRequest(BaseModel):
    user_input: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Neo4j API!"}

@app.post("/generate_query")
async def generate_query(request: QueryRequest):
    user_input = request.user_input.lower()
    logger.info(f"Received input query: {user_input}")

    # Get the schema
    schema = graph.schema

    # Initialize the LLM (Language Model)
    llm = ChatGroq(model_name="llama3-8b-8192")  # Use the model you want to deploy

    # Prepare the prompt for the model
    prompt = f"""
    The database schema is as follows:
    {schema}

    Please generate Cypher queries based on the schema.
    Example Question:
    What is total spending by Agency?

    Query Output:
    MATCH (a:Agency)-[:HAS_CONTRACT]->(c:Contract)
    RETURN a.name AS agency_name, ROUND(SUM(c.check_amount)) AS total_spending
    ORDER BY total_spending DESC
    LIMIT 5;

    Example Question:
    Who are the top 5 vendors by total spending?

    Query Output:
    MATCH (p:Payee)<-[:PAID_TO]-(c:Contract)
    RETURN p.name AS vendor_name, ROUND(SUM(c.check_amount)) AS total_spending
    ORDER BY total_spending DESC
    LIMIT 5;     

    Example Question:
    Which departments have the highest average spending per contract?

    Query Output:
    MATCH (d:Department)<-[:MANAGED_BY]-(c:Contract)
    RETURN d.name AS department, ROUND(AVG(c.check_amount)) AS average_spending
    ORDER BY average_spending DESC
    LIMIT 5;

    Example Question:
    What is the total spending for year 2021?

    Query Output:
    MATCH (c:Contract)
    WHERE c.fiscal_year = 2021
    RETURN ROUND(SUM(c.check_amount)) AS total_spending;

    Example Question:
    What is the spending by a specific Agency, such as Department of Education, in 2023?

    Query Output:
    MATCH (a:Agency)-[:HAS_CONTRACT]->(c:Contract)
    WHERE a.name = 'Department of Education' AND c.fiscal_year = 2023
    RETURN ROUND(SUM(c.check_amount)) AS total_spending;

    
    Do not generate queriy with GROUP BY in it.Only generate the Cypher query as response.
    """

    # Create a schema message and user query
    schema_message = HumanMessage(content=prompt)
    query_prompt = HumanMessage(content=user_input)  # User's question

    # Generate the response from the LLM
    response = llm([schema_message, query_prompt])
    
    # Log the generated Cypher query
    cypher_query = response.content
    logger.info(f"Generated Cypher Query:\n{cypher_query}")

    # Execute the generated Cypher query
    result = graph.query(cypher_query)
    results = [record for record in result]  # Collect results

    logger.info(f"Query Results:\n{results}")
    return {"query": cypher_query, "results": results}
