from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from collections import Counter

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

def analyze_skills(df):
    all_skills = [skill for skills_dict in df['skills'] for skill_list in skills_dict.values() for skill in skill_list]
    return Counter(all_skills)

def analyze_work_experience(df):
    all_experience = [exp for exps in df['work_experience'] for exp in exps]
    return Counter(all_experience)

def analyze_education(df):
    all_education = [edu for edus in df['education'] for edu in edus]
    return Counter(all_education)

def analyze_job_descriptions(df):
    topics = perform_topic_modeling(df)
    skills_analysis = analyze_skills(df)
    work_experience_analysis = analyze_work_experience(df)
    education_analysis = analyze_education(df)
    
    return {
        'topics': topics,
        'skills': skills_analysis,
        'work_experience': work_experience_analysis,
        'education': education_analysis
    }