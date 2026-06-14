from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skill_extractor import preprocess_text, find_missing_skills

def clean_and_stop_words(text):
    """Simple stopword removal without needing heavy NLTK downloads"""
    stopwords = set(["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"])
    
    clean_txt = preprocess_text(text)
    words = clean_txt.split()
    filtered = [w for w in words if w not in stopwords]
    return " ".join(filtered)

def calculate_match_score(job_desc_text, resume_text):
    """
    Computes percentage match using a Hybrid approach:
    70% Weighted Skill Matching + 30% TF-IDF Cosine Similarity.
    """
    # 1. Skill Matching Score (70% weight)
    skill_analysis = find_missing_skills(job_desc_text, resume_text)
    job_reqs = skill_analysis['job_req_all']
    res_matches = skill_analysis['res_has_all']
    
    # Calculate how many of the JOB'S required skills the candidate has
    # We only care about matching what the job actually asked for
    job_skills_set = set([s.lower() for s in job_reqs])
    res_skills_set = set([s.lower() for s in res_matches])
    
    matching_reqs = job_skills_set.intersection(res_skills_set)
    
    if len(job_skills_set) > 0:
        skill_score = (len(matching_reqs) / len(job_skills_set)) * 100
    else:
        skill_score = 50.0 # Neutral if no skills extracted from JD
        
    # 2. Text Similarity Score (30% weight)
    job_clean = clean_and_stop_words(job_desc_text)
    res_clean = clean_and_stop_words(resume_text)
    
    if not job_clean or not res_clean:
        text_score = 0.0
    else:
        documents = [job_clean, res_clean]
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            text_score = similarity_matrix[0][0] * 100
        except ValueError:
            text_score = 0.0
            
    # 3. Final Weighted Score
    # We give high priority to specific skill matches
    final_score = (skill_score * 0.7) + (text_score * 0.3)
    
    # Ensure the score isn't too punishing (Candidates with good skills should get 70+)
    # If skill match is high, we boost the lower bounds
    if skill_score > 80 and final_score < 80:
        final_score = 80 + (final_score * 0.1)

    return round(min(final_score, 100.0), 2)
