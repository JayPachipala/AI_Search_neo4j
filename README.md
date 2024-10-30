# AI Search 

# AI Search App

A web application that allows users to query a Neo4j graph database using natural language. The application uses FastAPI for the backend and React for the frontend, along with LLaMA to generate Cypher queries.

## Features

- Natural language query input
- Dynamic generation of Cypher queries
- Display results in both table and chart formats
- Previous questions and responses stored for reference

## Tech Stack

- **Frontend**: React
- **Backend**: FastAPI
- **Database**: Neo4j
- **Natural Language Processing**: LLaMA (via LangChain)
- **Data Visualization**: Recharts

## Installation

### Prerequisites

- Python 3.x
- Node.js
- Neo4j Database

### Backend Setup

1. Clone the repository:
  ```
   git clone https://github.com/yourusername/neo4j-query-interface.git
   cd neo4j-query-interface/backend
   ```
2. Create a virtual environment:
 ```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install the required Python packages:
```
pip install -r requirements.txt
```
4. Set up your environment variables:
```
export GROQ_API_KEY='your_groq_api_key'
export NEO4J_URI='bolt://localhost:7687'
export NEO4J_USERNAME='neo4j'
export NEO4J_PASSWORD='your_neo4j_password'
```
5. Run the FastAPI server:
```
uvicorn app:app --reload
```
6. Frontend Setup
Navigate to the frontend directory:
```
cd ../frontend
```
7. Install the required Node.js packages:
```
npm install
```
8. Start the React application:
```
npm start
```