import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# Constants for generation
JOB_TITLES = [
    'Data Scientist', 'Data Analyst', 'Software Engineer', 'Python Developer', 
    'Machine Learning Engineer', 'Web Developer', 'Business Analyst', 
    'Full Stack Developer', 'AI Engineer', 'Data Engineer', 'Cloud Architect', 
    'UI/UX Designer', 'DevOps Engineer', 'NLP Specialist', 'Cybersecurity Analyst'
]
COMPANIES = ['TechCorp', 'DataSolutions', 'InnovateAI', 'SoftSystems', 'AlphaTech', 'OmegaSol', 'FutureNet', 'CloudNine', 'NeuralBasis']
LOCATIONS = ['Bangalore', 'Mumbai', 'Hyderabad', 'Pune', 'Chennai', 'Delhi', 'Remote', 'Gurgaon', 'Noida']
SKILLS_POOL = ['Python', 'SQL', 'Java', 'C++', 'AWS', 'TensorFlow', 'Pandas', 'Spark', 'Excel', 'Tableau', 'React', 'Node.js', 'Power BI', 'Docker', 'Kubernetes', 'Azure', 'GCP', 'Flutter', 'Figma']

def generate_description(title):
    """Generates a pseudo-random job description containing highly specific skills."""
    base_desc = f"We are looking for a dedicated {title} to join our tech division. "
    
    # Define exact, non-overlapping skill pools for high accuracy
    if 'Web Developer' in title:
        relevant_skills = ['JavaScript', 'React', 'Node.js', 'HTML/CSS', 'TypeScript', 'Tailwind CSS', 'Redux', 'REST API']
    elif 'Software Engineer' in title:
        relevant_skills = ['Java', 'C++', 'Python', 'C#', 'Algorithms', 'Data Structures', 'System Design', 'Linux']
    elif 'Data Scientist' in title:
        relevant_skills = ['Python', 'Statistics', 'Pandas', 'NumPy', 'Scikit-Learn', 'Feature Engineering', 'Jupyter', 'Data Visualization']
    elif 'Machine Learning' in title or 'AI Engineer' in title:
        relevant_skills = ['Python', 'TensorFlow', 'PyTorch', 'Neural Networks', 'MLOps', 'AWS Sagemaker', 'Model Deployment', 'NLP']
    elif 'Data Analyst' in title:
        relevant_skills = ['SQL', 'Excel', 'Tableau', 'Power BI', 'Google Data Studio', 'Metabase', 'Data Cleaning', 'Reporting']
    elif 'Python Developer' in title:
        relevant_skills = ['Python', 'Django', 'Flask', 'FastAPI', 'Pytest', 'Celery', 'PostgreSQL', 'Redis']
    elif 'Full Stack Developer' in title:
        relevant_skills = ['React', 'Node.js', 'Express', 'MongoDB', 'Next.js', 'PostgreSQL', 'Docker', 'Git']
    elif 'DevOps' in title:
        relevant_skills = ['Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'CI/CD', 'Ansible', 'Bash', 'AWS']
    elif 'UI/UX' in title:
        relevant_skills = ['Figma', 'Adobe XD', 'User Research', 'Wireframing', 'Color Theory', 'Prototyping', 'Responsive Design']
    elif 'Cloud Architect' in title:
        relevant_skills = ['AWS', 'Azure', 'GCP', 'IAM', 'VPC', 'Serverless', 'Microservices', 'Cloud Migration']
    elif 'Data Engineer' in title:
        relevant_skills = ['Spark', 'Hadoop', 'Kafka', 'Airflow', 'ETL', 'Snowflake', 'Dbt', 'SQL']
    elif 'Cybersecurity' in title:
        relevant_skills = ['Penetration Testing', 'SIEM', 'IDS/IPS', 'Cryptography', 'Vulnerability Assessment', 'Firewalls', 'Security Audit']
    else:
        relevant_skills = SKILLS_POOL

    # Select 4-6 skills to ensure variety but high role correlation
    k = min(len(relevant_skills), random.randint(4, 6))
    required_skills = random.sample(relevant_skills, k=k)
    
    # Role-specific forcing
    if 'Python' in title and 'Python' not in required_skills:
        required_skills[0] = 'Python'
    if 'Web' in title and 'HTML/CSS' not in required_skills:
        required_skills[-1] = 'HTML/CSS'

    desc = base_desc + "The ideal candidate should be proficient in " + ", ".join(required_skills) + ". "
    desc += "Must be capable of working in an agile environment and delivering high-quality code."
    return desc, required_skills

def generate_dataset(num_rows=20000):
    data = []
    
    for i in range(num_rows):
        job_id = i + 1001
        title = random.choice(JOB_TITLES)
        company = random.choice(COMPANIES)
        location = random.choice(LOCATIONS)
        
        desc, skills_truth = generate_description(title)

        # Salary correlated with role type
        if 'Engineer' in title or 'Scientist' in title or 'Architect' in title:
            base_salary = 900000
        elif 'Developer' in title:
            base_salary = 700000
        else:
            base_salary = 500000
            
        salary = base_salary + (len(skills_truth) * 60000) + random.randint(-50000, 150000)
        
        # Random date within last year
        date_posted = datetime.now() - timedelta(days=random.randint(0, 365))
        
        row = {
            'Job_ID': job_id,
            'Job_Title': title,
            'Company': company,
            'Location': location,
            'Job_Description': desc,
            'Salary_INR': salary,
            'Date_Posted': date_posted.strftime('%Y-%m-%d'),
            'Skills_JSON': skills_truth
        }
        data.append(row)
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Generating Role-Specific Market Data (20,000 jobs)...")
    df = generate_dataset(20000)
    
    # Save to CSV
    output_path = 'data/job_market_data.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Data saved successfully to: {output_path}")
    print(f"Dataset Shape: {df.shape}")
    print("\nPreview of exact role skills:")
    print(df[['Job_Title', 'Skills_JSON']].head(10))
