import pandas as pd
import json
import os
import re
from preprocess import load_data, preprocess_job_descriptions
from extract import load_config, extract_information
from analyze import analyze_job_descriptions

def flatten_skills(skills_dict):
    return ', '.join(set([item.lower() for sublist in skills_dict.values() for item in sublist]))

def ensure_dict(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {x}")
            return {}
    return x

def extract_years_of_experience(text):
    experience_pattern = r'\b(\d+(?:\+|\s*-\s*\d+)?)\s*(?:years?|yrs?)\b'
    matches = re.findall(experience_pattern, text, re.IGNORECASE)
    if matches:
        years = [int(num) for match in matches for num in re.findall(r'\d+', match)]
        return f"{min(years)}-{max(years)}" if len(set(years)) > 1 else str(max(years))
    return None

def capitalize_skills(skills_string):
    skill_list = skills_string.split(', ')
    capitalize_list = ['sql', 'python', 'r', 'bi', 'aws', 'excel']
    return ', '.join(skill.upper() if skill.lower() in capitalize_list else skill.capitalize() for skill in skill_list)

def main():
    df = load_data('data/raw/cleaned_job_details.csv')
    df = preprocess_job_descriptions(df)
    config = load_config('config/config.yaml')
    df = extract_information(df, config)
    
    df['skills'] = df['skills'].apply(ensure_dict)
    df['years_of_experience'] = df['Job Description'].apply(extract_years_of_experience)
    df['hard_skills'] = df['skills'].apply(lambda x: flatten_skills({k: v for k, v in x.items() if k != 'soft_skills'}))
    df['hard_skills'] = df['hard_skills'].apply(capitalize_skills)
    
    df = df[(df['hard_skills'] != '')]
    
    final_columns = [
        'Company Name', 'Company Link', 'Job Title', 'Job Link', 'City', 'State', 'Country',
        'years_of_experience', 'hard_skills'
    ]
    final_df = df[final_columns]
    
    output_dir = 'data/processed'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'processed_job_skills.csv')
    final_df.to_csv(output_file, index=False)
    print(f"Processing complete. Results saved to {output_file}")
    
    analysis_results = analyze_job_descriptions(df)
    json_output_file = os.path.join(output_dir, 'analysis_summary.json')
    with open(json_output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    print(f"Analysis summary saved to {json_output_file}")

if __name__ == "__main__":
    main()