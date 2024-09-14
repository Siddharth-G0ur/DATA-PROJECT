from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def perform_topic_modeling(df, n_topics=5, n_top_words=10):
    vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
    doc_term_matrix = vectorizer.fit_transform(df['processed_description'])
    
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(doc_term_matrix)
    
    feature_names = vectorizer.get_feature_names_out()
    return get_top_words_per_topic(lda, feature_names, n_top_words)

def get_top_words_per_topic(model, feature_names, n_top_words):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        topics.append(top_words)
    return topics

def analyze_job_descriptions(df):
    topics = perform_topic_modeling(df)
    
    # Add more analysis functions here as needed
    
    return {
        'topics': topics,
        # Add more analysis results here
    }