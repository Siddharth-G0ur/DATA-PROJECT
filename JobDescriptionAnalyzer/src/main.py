import pandas as pd
import json
import os
import re
from preprocess import load_data, preprocess_job_descriptions
from extract import load_config, extract_information
from analyze import analyze_job_descriptions

def flatten_skills(skills_dict):
    """Flattens the nested skills dictionary into a comma-separated string."""
    return ', '.join(set([item.lower() for sublist in skills_dict.values() for item in sublist]))

def ensure_dict(x):
    """Ensures that the value is a dictionary. If it's a string, try to convert it to a dictionary."""
    if isinstance(x, str):
        try:
            return json.loads(x)
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {x}")
            return {}
    return x

def extract_years_of_experience(text):
    """Extracts years of experience from the job description."""
    experience_pattern = r'\b(\d+(?:\+|\s*-\s*\d+)?)\s*(?:years?|yrs?)\b'
    matches = re.findall(experience_pattern, text, re.IGNORECASE)
    if matches:
        # Extract all numbers from matches
        years = [int(num) for match in matches for num in re.findall(r'\d+', match)]
        return f"{min(years)}-{max(years)}" if len(set(years)) > 1 else str(max(years))
    return None

def capitalize_skills(skills_string):
    """Capitalizes common acronyms and programming languages."""
    skill_list = skills_string.split(', ')
    capitalize_list = ['sql', 'python', 'r', 'bi', 'aws', 'excel']
    return ', '.join(skill.upper() if skill.lower() in capitalize_list else skill.capitalize() for skill in skill_list)

def main():
    # Load and preprocess data
    df = load_data('data/raw/cleaned_job_details.csv')
    df = preprocess_job_descriptions(df)
    
    # Load configuration
    config = load_config('config/config.yaml')
    
    # Extract information from job descriptions
    df = extract_information(df, config)
    
    # Ensure 'skills' column is in dictionary format
    df['skills'] = df['skills'].apply(ensure_dict)

    # Extract years of experience
    df['years_of_experience'] = df['Job Description'].apply(extract_years_of_experience)

    # Prepare new columns for hard skills and soft skills
    df['hard_skills'] = df['skills'].apply(lambda x: flatten_skills({k: v for k, v in x.items() if k != 'soft_skills'}))
    df['soft_skills'] = df['skills'].apply(lambda x: ', '.join(set(x.get('soft_skills', []))) if isinstance(x, dict) else '')

    # Capitalize skills
    df['hard_skills'] = df['hard_skills'].apply(capitalize_skills)
    df['soft_skills'] = df['soft_skills'].apply(capitalize_skills)

    # Remove rows with empty skills
    df = df[(df['hard_skills'] != '') | (df['soft_skills'] != '')]

    # Select and reorder columns for the final output
    final_columns = [
        'Company Name', 'Job Title', 'years_of_experience', 'hard_skills', 'soft_skills'
    ]
    
    # Create the final dataframe with the selected columns
    final_df = df[final_columns]
    
    # Ensure the output directory exists
    output_dir = 'data/processed'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the final dataframe to a CSV file
    output_file = os.path.join(output_dir, 'processed_job_skills.csv')
    final_df.to_csv(output_file, index=False)
    
    print(f"Processing complete. Results saved to {output_file}")

    # Perform analysis on job descriptions (optional)
    analysis_results = analyze_job_descriptions(df)
    
    # Save analysis results (optional)
    json_output_file = os.path.join(output_dir, 'analysis_summary.json')
    with open(json_output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"Analysis summary saved to {json_output_file}")

if __name__ == "__main__":
    main()