import spacy
import yaml
from collections import defaultdict
import re

nlp = spacy.load("en_core_web_sm")

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def extract_skills(text, skill_keywords):
    doc = nlp(text.lower())
    skills = defaultdict(set)  # Changed to set for automatic deduplication
    for category, keywords in skill_keywords.items():
        for keyword in keywords:
            if keyword.lower() in doc.text:
                skills[category].add(keyword.lower())
    return {k: list(v) for k, v in skills.items()}  # Convert sets back to lists

def extract_work_experience(text):
    experience_patterns = [
        r'\d+\+?\s*(?:-\s*\d+\s*)?(?:year|yr)s?\s*(?:of\s*)?experience',
        r'(?:minimum|min|at least)\s*\d+\s*(?:year|yr)s?\s*(?:of\s*)?experience',
        r'experience\s*(?:of|for)\s*\d+\+?\s*(?:year|yr)s?'
    ]
    experiences = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, text.lower())
        experiences.extend(matches)
    return list(set(experiences))  # Remove duplicates

def extract_education(text):
    education_patterns = [
        r"bachelor'?s?\s*degree",
        r"master'?s?\s*degree",
        r"ph\.?d\.?",
        r"doctorate",
        r"high school diploma",
        r"associate'?s?\s*degree"
    ]
    educations = []
    for pattern in education_patterns:
        matches = re.findall(pattern, text.lower())
        educations.extend(matches)
    return list(set(educations))  # Remove duplicates

def extract_information(df, config):
    skill_keywords = config['skills_keywords']
    df['skills'] = df['processed_description'].apply(lambda x: extract_skills(x, skill_keywords))
    df['work_experience'] = df['Job Description'].apply(extract_work_experience)
    df['education'] = df['Job Description'].apply(extract_education)
    return df