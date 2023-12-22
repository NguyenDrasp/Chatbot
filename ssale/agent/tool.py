import os
import openai
import requests
import datetime
import wikipedia
import pinecone
import tqdm 
from langchain.tools import tool
from pydantic.v1 import BaseModel, Field
from dotenv import load_dotenv, find_dotenv
from langchain.utilities import SQLDatabase
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.vectorstores import Pinecone
from .agent import CustomAsyncCallbackHandler

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']



class OpenMeteoInput(BaseModel):
    latitude: float = Field(..., description="Latitude of the location to fetch weather data for")
    longitude: float = Field(..., description="Longitude of the location to fetch weather data for")


@tool(args_schema=OpenMeteoInput)
def get_current_temperature(latitude: float, longitude: float) -> dict:
    """Fetch current temperature for given coordinates."""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Parameters for the request
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': 'temperature_2m',
        'forecast_days': 1,
    }

    # Make the request
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        results = response.json()
    else:
        raise Exception(f"API Request failed with status code: {response.status_code}")

    current_utc_time = datetime.datetime.utcnow()
    time_list = [datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00')) for time_str in results['hourly']['time']]
    temperature_list = results['hourly']['temperature_2m']
    
    closest_time_index = min(range(len(time_list)), key=lambda i: abs(time_list[i] - current_utc_time))
    current_temperature = temperature_list[closest_time_index]
    
    return f'The current temperature is {current_temperature}°C'

#----------------------------------------------------------------------------------------------------------------------------

@tool
def search_wikipedia(query:str) -> str:
    """Run Wikipedia search and get page summaries."""
    page_titles = wikipedia.search(query)
    summaries = []
    for page_title in page_titles[: 3]:
        try:
            wiki_page =  wikipedia.page(title=page_title, auto_suggest=False)
            summaries.append(f"Page: {page_title}\nSummary: {wiki_page.summary}")
        except (
            self.wiki_client.exceptions.PageError,
            self.wiki_client.exceptions.DisambiguationError,
        ):
            pass
    if not summaries:
        return "No good Wikipedia Search Result was found"
    return "\n\n".join(summaries)

#----------------------------------------------------------------------------------------------------------------------------
#Tạo trước SQL query tool
template = """Based on the table schema below, write a SQL query that would answer the user's question:
{schema}
Question: {question}
SQL Query:"""
prompt = ChatPromptTemplate.from_template(template)
db = SQLDatabase.from_uri("sqlite:///db.sqlite3")

def get_schema(_):
    return db.get_table_info()

def run_query(query):
    return db.run(query)

model = ChatOpenAI()

sql_response = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | model.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)

template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
{schema}

Question: {question}
SQL Query: {query}
SQL Response: {response}"""
prompt_response = ChatPromptTemplate.from_template(template)

full_chain = (
RunnablePassthrough.assign(query=sql_response)
| RunnablePassthrough.assign(
    schema=get_schema,
    response=lambda x: db.run(x["query"]),
)
| prompt_response
| model
)

@tool
def sqlQuery(question:str) -> str:
    """Useful when you need to answer any questions about the MDC software store and its apps. It use an query agent to get the answers"""   
    return full_chain.invoke({"question": question}).content

#----------------------------------------------------------------------------------------------------------------------------

# Tạo trước RetrievalTool
def createRetrieval():
    embeddings = OpenAIEmbeddings()
    # initialize pinecone
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
        environment=os.getenv("PINECONE_ENV"),  # next to api key in console
    )

    index_name = "klook"

    # First, check if our index already exists. If it doesn't, we create it
    if index_name not in pinecone.list_indexes():
        # we create a new index
        pinecone.create_index(
        name=index_name,
        metric='cosine',
        dimension=1536
    )
    index = pinecone.Index(index_name)
    docsearch = Pinecone(index, embeddings.embed_query, "text")
    retriever = docsearch.as_retriever()

    return retriever
