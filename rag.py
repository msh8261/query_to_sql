import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from log import logger



# Initialize ChromaDB client and embedding model
client = chromadb.Client()

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Define a class to wrap the embedding function
class ChromaEmbeddingFunction:
    def __call__(self, input):
        try:
            # Ensure the input is a list of strings and encode it
            return embedding_model.encode(input)
        except Exception as e:
            logger.error(f"Error in encoding input: {e}")
            raise

# Create an instance of the embedding function class
embedding_function = ChromaEmbeddingFunction()

# Create ChromaDB collection for schema metadata
try:
    schema_collection = client.create_collection(
        name="schema_metadata",
        embedding_function=embedding_function,  # Pass the embedding function class
    )
    logger.info("ChromaDB collection created successfully.")
except Exception as e:
    logger.error(f"Error creating ChromaDB collection: {e}")
    raise

def store_schema_in_chromadb(schema_data):
    try:
        # Prepare schema data for ChromaDB
        for schema in schema_data:
            try:
                # Generate embedding for schema description
                schema_embedding = embedding_model.encode([schema['description']])[0]
                logger.info(f"Generated embedding for schema {schema['id']}: {schema_embedding}")  # Log the generated embedding

                metadata = {
                    'columns': 'id, name, email, age',  # Use a single string that describes the columns
                    'table': 'users'  # Add table name to match later
                }

                schema_collection.add(
                    documents=[schema['description']],  # Schema description or relevant info
                    metadatas=[metadata],  # Correct metadata format
                    ids=[str(schema['id'])],  # Unique ID for each record
                    embeddings=[schema_embedding]  # Use the actual generated embedding
                )
                logger.info(f"Schema {schema['id']} stored successfully.")
            except Exception as e:
                logger.error(f"Error processing schema {schema['id']}: {e}")
    except Exception as e:
        logger.error(f"Error storing schema in ChromaDB: {e}")
        raise


# Example schema data (the descriptions will be used to generate the embeddings)
schema_data = [
    {
        'id': 1,
        'column_name': 'id',
        'data_type': 'INTEGER',
        'description': 'Unique identifier for each row',
    },
    {
        'id': 2,
        'column_name': 'name',
        'data_type': 'VARCHAR',
        'description': 'Name of the user',
    },
    # Add more schema entries as needed
]

store_schema_in_chromadb(schema_data)


# Function to retrieve schema based on query
def retrieve_schema_from_chromadb(query):
    try:
        query_embedding = embedding_model.encode([query])[0]
        results = schema_collection.query(
            query_embeddings=[query_embedding],
            n_results=1
        )
        return results['metadatas'][0]
    except Exception as e:
        logger.error(f"Error retrieving schema for query '{query}': {e}")
        raise


def generate_sql_from_query(query, params=None):
    schema_info = schema_collection.get()

    for metadata in schema_info['metadatas']:
        if isinstance(metadata, dict):
            if 'table' in metadata and 'users' in metadata['table']:
                # Split columns into a list
                columns = metadata['columns'].split(", ")
                
                # Initialize where clause as an empty list
                where_clause = []
                
                # Loop through the query to handle conditions dynamically
                if "over 30" in query:
                    where_clause.append(f"age > ?")
                else:
                    # Add a condition for each column
                    where_clause = [f"{col} = ?" for col in columns]
                
                # Join conditions with 'AND'
                where_clause = " AND ".join(where_clause)

                # Construct the SQL query
                sql_query = f"SELECT * FROM {metadata['table']} WHERE {where_clause}"

                # Replace placeholders with params
                if params:
                    sql_query = sql_query.replace("?", "%s")  # For PostgreSQL-style placeholders
                    return sql_query, params  # Return SQL with params for execution

    return None, None  # Return None if no matching schema is found



def generate_dynamic_sql(query, params=None):
    sql_query = generate_sql_from_query(query, params)
    if sql_query:
        return sql_query
    else:
        return "Query could not be generated"

def handle_user_query(query, params=None):
    sql_query = generate_dynamic_sql(query, params)
    return sql_query



if __name__ == "__main__":
    # Example usage:
    try:
        query = "Show me all employees and their departments"
        params = [30]  # Add actual values here for placeholders
        sql, final_params = handle_user_query(query, params)
        print("Generated SQL:", sql)
        print("With parameters:", final_params)
    except Exception as e:
        logger.error(f"Error during execution: {e}")
