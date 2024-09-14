import spacy
import yaml

nlp = spacy.load("en_core_web_sm")

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def extract_skills(text, skill_keywords):
    doc = nlp(text.lower())
    skills = [token.text for token in doc if token.text in skill_keywords or token.lemma_ in skill_keywords]
    return list(set(skills))

def extract_work_experience(text):
    doc = nlp(text)
    experience = []
    for ent in doc.ents:
        if ent.label_ == "DATE" and "year" in ent.text.lower():
            experience.append(ent.text)
    return experience

def extract_education(text):
    education_keywords = ["bachelor", "master", "phd", "degree"]
    doc = nlp(text.lower())
    education = [sent.text for sent in doc.sents if any(keyword in sent.text for keyword in education_keywords)]
    return education

def extract_information(df, config):
    skill_keywords = config['skills_keywords']
    
    df['skills'] = df['processed_description'].apply(lambda x: extract_skills(x, skill_keywords))
    df['work_experience'] = df['Job Description'].apply(extract_work_experience)
    df['education'] = df['Job Description'].apply(extract_education)
    
    return df