import streamlit as st
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Initialize Pinecone
pc = Pinecone(api_key="8fa5b9fd-2008-4306-b992-d86773b06ab3")

# Connect to the index
index_name = "job-search"
index = pc.Index(index_name)

# Initialize SentenceTransformer model
@st.cache_resource
def load_model():
    return SentenceTransformer('intfloat/multilingual-e5-large')

model = load_model()

def search_jobs(query, top_k=5):
    # Generate query embedding
    query_embedding = model.encode([query])[0]
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_values=False,
        include_metadata=True
    )
    
    return results

st.title("Job Search App")

query = st.text_input("Enter your job search query:")

if query:
    results = search_jobs(query)
    
    for result in results['matches']:
        st.subheader(result['metadata']['job_title'])
        st.write(f"Company: {result['metadata']['company_name']}")
        st.write(f"Sector: {result['metadata']['company_sector']}")
        st.write(f"Location: {result['metadata']['location']}")
        st.write(f"Company Size: {result['metadata']['company_size']}")
        st.write(f"Job Link: {result['metadata']['job_link']}")
        st.write(f"Similarity Score: {result['score']:.2f}")
        st.markdown("---")