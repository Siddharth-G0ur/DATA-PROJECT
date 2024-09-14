import pandas as pd
from preprocess import load_data, preprocess_job_descriptions
from extract import load_config, extract_information
from analyze import analyze_job_descriptions

def main():

    df = load_data('data/raw/cleaned_job_details.csv')
    df = preprocess_job_descriptions(df)
    
    config = load_config('config/config.yaml')
    
    df = extract_information(df, config)
    
    analysis_results = analyze_job_descriptions(df)
    
    print("Top skills across all job descriptions:")
    print(df['skills'].explode().value_counts().head(10))
    
    print("\nMost common work experience requirements:")
    print(df['work_experience'].explode().value_counts().head(5))
    
    print("\nMost common education requirements:")
    print(df['education'].explode().value_counts().head(5))
    
    print("\nTopics discovered through LDA:")
    for i, topic in enumerate(analysis_results['topics']):
        print(f"Topic {i + 1}: {', '.join(topic)}")

if __name__ == "__main__":
    main()