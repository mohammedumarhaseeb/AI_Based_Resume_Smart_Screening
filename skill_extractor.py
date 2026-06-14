import re

# Load the spacy model for lemmatization
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except (OSError, ImportError):
    # Fallback if model not found or blocked by policy
    nlp = None

# Comprehensive list of standard tech & soft skills
TECHNICAL_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "react", "angular", "vue",
    "sql", "mysql", "postgresql", "mongodb", "aws", "azure", "gcp", "docker",
    "kubernetes", "linux", "git", "machine learning", "deep learning", "nlp",
    "tensorflow", "pytorch", "scikit-learn", "data analysis", "data science",
    "html", "css", "django", "flask", "spring boot", "nodejs", "express",
    "pandas", "numpy", "api", "rest", "graphql"
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving", 
    "critical thinking", "adaptability", "time management", "collaboration",
    "conflict resolution", "creativity", "work ethic", "management", "mentoring"
]

def preprocess_text(text):
    """Lowercases text, removes punctuation, and lemmatizes using spaCy if available."""
    if not text:
        return ""
    text = text.lower()
    # Replace punctuation with spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    if nlp:
        doc = nlp(text)
        return " ".join([token.lemma_ for token in doc])
    return text

def extract_skills(text):
    """
    Extracts explicit Technical and Soft skills found in the text.
    Returns a dictionary.
    """
    clean_text = preprocess_text(text)
    words = set(clean_text.split())
    
    found_tech = set()
    for skill in TECHNICAL_SKILLS:
        # For multi-word skills like "machine learning"
        if " " in skill:
            if f" {skill} " in f" {clean_text} ":
                found_tech.add(skill.title())
        elif skill in words:
            found_tech.add(skill.title())
            
    found_soft = set()
    for skill in SOFT_SKILLS:
        if " " in skill:
            if f" {skill} " in f" {clean_text} ":
                found_soft.add(skill.title())
        elif skill in words:
            found_soft.add(skill.title())
            
    return {
        "technical": list(found_tech),
        "soft": list(found_soft),
        "all": list(found_tech) + list(found_soft)
    }

def find_missing_skills(job_text, resume_text):
    """Finds what skills the Job asks for that the Resume lacks."""
    job_skills_dict = extract_skills(job_text)
    resume_skills_dict = extract_skills(resume_text)
    
    job_tech_skills = set([s.lower() for s in job_skills_dict['technical']])
    res_tech_skills = set([s.lower() for s in resume_skills_dict['technical']])
    
    job_soft_skills = set([s.lower() for s in job_skills_dict['soft']])
    res_soft_skills = set([s.lower() for s in resume_skills_dict['soft']])
    
    missing_tech = job_tech_skills - res_tech_skills
    missing_soft = job_soft_skills - res_soft_skills
    
    # Title-case for display
    return {
        "technical": [s.title() for s in missing_tech],
        "soft": [s.title() for s in missing_soft],
        "job_req_all": list(set([s.title() for s in job_tech_skills.union(job_soft_skills)])),
        "res_has_all": list(set([s.title() for s in res_tech_skills.union(res_soft_skills)]))
    }
