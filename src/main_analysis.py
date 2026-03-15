import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import spacy
import os

# Set global constraints
DATA_PATH = "data/job_market_data.csv"
OUTPUT_DIR = "output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Loads the dataset."""
    if not os.path.exists(DATA_PATH):
        print("Data file not found. Please run mock_data_generator.py first.")
        return None
    df = pd.read_csv(DATA_PATH)
    if 'Salary' in df.columns and 'Salary_INR' not in df.columns:
        df.rename(columns={'Salary': 'Salary_INR'}, inplace=True)
    print(f"Data Loaded: {df.shape[0]} records.")
    return df

def extract_skills_nlp(text, nlp_model=None):
    """
    Extracts skills from text using a robust regex-based matching system.
    Handles special characters like C++, Node.js, and Power BI.
    """
    detected_skills = []
    
    # Comprehensive skill set from utils
    import utils
    known_skills = utils.GET_MASTER_SKILLS()
    
    # Normalize text: convert to lowercase and remove multiple spaces
    text_normalized = " " + text.lower() + " "
    text_normalized = re.sub(r'\s+', ' ', text_normalized)
    
    for skill in known_skills:
        # Improved Regex:
        # Look for the skill surrounded by boundary markers (space, punctuation, or start/end of string)
        # We use lookarounds to handle skills with special characters like 'c++'
        pattern = r'(?i)(?<=[\s,./()\-]|[^\w\d])' + re.escape(skill) + r'(?=[\s,./()\-]|[^\w\d]|$)'
        
        if re.search(pattern, text_normalized):
            detected_skills.append(skill)
            
    return sorted(list(set(detected_skills)))

def analyze_trends(df):
    """Performs descriptive analytics on skills."""
    all_skills = []
    for skills in df['Extracted_Skills']:
        all_skills.extend(skills)
        
    skill_counts = Counter(all_skills)
    common_skills = skill_counts.most_common(10)
    
    print("\n--- Top 10 Trending Skills ---")
    for skill, count in common_skills:
        print(f"{skill.capitalize()}: {count}")
        
    # Visualization: Bar Chart
    plt.figure(figsize=(10, 6))
    skills, counts = zip(*common_skills)
    plt.bar(skills, counts, color='skyblue')
    plt.title('Top 10 In-Demand Skills')
    plt.xlabel('Skills')
    plt.ylabel('Frequency')
    plt.savefig(f"{OUTPUT_DIR}/top_skills.png")
    print(f"Saved chart: {OUTPUT_DIR}/top_skills.png")
    
    return skill_counts

def skill_gap_analysis(user_skills, market_skills_counter, job_role_filter=None):
    """
    Identifies the gap between user skills and market demand.
    """
    print(f"\n--- Skill Gap Analysis for '{job_role_filter}' ---")
    print(f"User Skills: {user_skills}")
    
    # In a real app, we would filter market_skills_counter by job_role first
    # Here we assume market_skills_counter represents the target market
    
    market_top_20 = [s for s, c in market_skills_counter.most_common(20)]
    
    missing_skills = [s for s in market_top_20 if s not in user_skills]
    
    print("Identified Skill Gaps (High Priority):")
    for skill in missing_skills[:5]: # Top 5 missing
        print(f"- {skill.capitalize()}")
        
    return missing_skills

def predict_salary(df):
    """
    Simple Linear Regression to predict salary based on number of skills required.
    Demonstrates Predictive Analytics.
    """
    print("\n--- Salary Prediction Model ---")
    
    # Feature Engineering: Count of skills
    df['Skill_Count'] = df['Extracted_Skills'].apply(len)
    
    X = df[['Skill_Count']]
    y = df['Salary_INR']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    print(f"Model R^2 Score (Explanation Variance): {score:.2f}")
    
    # Prediction Example
    example_skill_count = pd.DataFrame({'Skill_Count': [3, 5, 7]})
    predictions = model.predict(example_skill_count)
    
    print("Predicted Salaries:")
    for count, salary in zip(example_skill_count['Skill_Count'], predictions):
        print(f"Skills: {count} -> Predicted Salary: INR {salary:.2f}")

def main():
    print("Initializing CareerGraph AI: Industry Skill Gap Intelligence System...")
    
    # 1. Load Data
    df = load_data()
    if df is None: return

    # 2. Preprocessing & Skill Extraction (NLP part)
    print("Extracting skills from job descriptions...")
    # we pass None for model to use fallback keyword matching for simplicity/speed
    df['Extracted_Skills'] = df['Job_Description'].apply(lambda x: extract_skills_nlp(x)) 
    
    # 3. Descriptive Analytics
    skill_counts = analyze_trends(df)
    
    # 4. Diagnostic Analytics (Gap Analysis)
    # Simulate a user profile
    user_profile = ['python', 'sql'] 
    skill_gap_analysis(user_profile, skill_counts, job_role_filter="Data Scientist")
    
    # 5. Predictive Analytics
    predict_salary(df)
    
    print("\nAnalysis Complete. Check 'output' folder for visuals.")

if __name__ == "__main__":
    main()
