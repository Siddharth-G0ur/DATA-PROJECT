import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm
from sentence_transformers import SentenceTransformer
import time

# Load the data
df = pd.read_csv('cleaned_job_details.csv')

# Initialize Pinecone
pc = Pinecone(api_key="8fa5b9fd-2008-4306-b992-d86773b06ab3")

# Create index if it doesn't exist
index_name = "job-search"
dimension = 1024  # Dimension for 'multilingual-e5-large' model

def create_index_if_not_exists():
    try:
        if index_name not in pc.list_indexes():
            print(f"Creating index '{index_name}'...")
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"Index '{index_name}' created successfully.")
        else:
            print(f"Index '{index_name}' already exists.")
    except Exception as e:
        if "ALREADY_EXISTS" in str(e):
            print(f"Index '{index_name}' already exists. Proceeding with the existing index.")
        else:
            raise e

create_index_if_not_exists()

# Connect to the index
index = pc.Index(index_name)

# Check if the index is empty
stats = index.describe_index_stats()
if stats.total_vector_count == 0:
    print("The index is empty. Proceeding with data insertion.")
else:
    user_input = input(f"The index '{index_name}' already contains {stats.total_vector_count} vectors. Do you want to (r)eset the index or (c)ontinue with the existing data? (r/c): ").lower()
    if user_input == 'r':
        print("Resetting the index...")
        index.delete(delete_all=True)
        time.sleep(5)  # Wait for the deletion to propagate
    elif user_input == 'c':
        print("Continuing with the existing data.")
    else:
        print("Invalid input. Exiting.")
        exit()

# Initialize SentenceTransformer model
model = SentenceTransformer('intfloat/multilingual-e5-large')

def prepare_job_data(df):
    job_data = []
    for _, row in df.iterrows():
        text_for_embedding = f"{row['Job Title']} {row['Company Sector']} {row['Job Description']}"
        job_data.append({
            "id": str(row.name),
            "text": text_for_embedding,
            "metadata": {
                "job_title": row['Job Title'],
                "company_name": row['Company Name'],
                "company_sector": row['Company Sector'],
                "location": f"{row['City']}, {row['State']}, {row['Country']}",
                "company_size": row['Company Size'],
                "job_link": row['Job Link']
            }
        })
    return job_data

# Prepare job data
job_data = prepare_job_data(df)

# Generate embeddings and upsert to Pinecone
batch_size = 100
for i in tqdm(range(0, len(job_data), batch_size)):
    batch = job_data[i:i+batch_size]
    
    # Generate embeddings using SentenceTransformer
    texts = [d['text'] for d in batch]
    embeddings = model.encode(texts)
    
    # Prepare vectors for upsert
    vectors = [
        (d['id'], e.tolist(), d['metadata']) for d, e in zip(batch, embeddings)
    ]
    
    # Upsert to Pinecone
    index.upsert(vectors=vectors)

def search_jobs(query, top_k=5):
    # Generate query embedding using SentenceTransformer
    query_embedding = model.encode([query])[0]
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_values=False,
        include_metadata=True
    )
    
    return results

# Example usage
query = "find me jobs in consultancy firms that require SQL and Python skills"
search_results = search_jobs(query)

for result in search_results['matches']:
    print(f"Job Title: {result['metadata']['job_title']}")
    print(f"Company: {result['metadata']['company_name']}")
    print(f"Sector: {result['metadata']['company_sector']}")
    print(f"Location: {result['metadata']['location']}")
    print(f"Job Link: {result['metadata']['job_link']}")
    print(f"Similarity Score: {result['score']}")
    print("---")