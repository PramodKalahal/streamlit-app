# Methodology and Data Analytics Techniques

## 5. Step-by-Step Methodology

1.  **Data Acquisition:** 
    - Simulate/Acquire a dataset of 1000+ job postings across various domains (IT, Finance, Marketing).
    - Store raw data in MySQL/CSV.

2.  **Data Preprocessing (ETL):**
    - **Cleaning:** Remove duplicates, handle null values in 'Salary' or 'Location'.
    - **NLP Pipeline:** Convert 'Job_Description' to lowercase, remove stop words, remove punctuation.
    - **Tokenization:** Break text into individual words/tokens.

3.  **Feature Engineering & Skill Extraction:**
    - Use a predefined dictionary of skills or Named Entity Recognition (spaCy) to identify skills in the text.
    - Create a 'One-Hot Encoded' or 'Frequency Matrix' of skills per job role.

4.  **Exploratory Data Analysis (EDA):**
    - Calculate frequency counts of skills.
    - Group by 'Job_Title' to find top skills per role.

5.  **Gap Analysis Implementation:**
    - Input: User's skill list.
    - Comparison: Compare User List vs. Top Required Skills for the target role.
    - Output: Missing skills sorted by importance (frequency).

6.  **Predictive Modeling:**
    - Prepare time-series data (Skill counts over months/years).
    - Train Linear Regression or ARIMA models to forecast skill popularity.

7.  **Visualization:**
    - Export processed results to CSV for Power BI.
    - Generate static plots using Matplotlib/Seaborn.

---

## 6. Data Analytics Techniques Used

1.  **Descriptive Analytics:**
    - **What happened?**
    - Analyzing historical data to show "Top 10 Most In-Demand Skills in 2025" or "Average Salary by Location".
    - Techniques: Aggregation, Frequency Distribution, Mean/Median Analysis.

2.  **Diagnostic Analytics:**
    - **Why did it happen?** (or in this context, "Where am I lacking?")
    - Identifying the root cause of a user's low employability score by comparing their profile to successful profiles.
    - Techniques: Correlation analysis, Similarity measures (Jaccard Index).

3.  **Predictive Analytics:**
    - **What will happen?**
    - Forecasting future trends using historical patterns.
    - Techniques: Time Series Analysis, Regression Analysis.

4.  **Prescriptive Analytics:**
    - **How can we make it happen?**
    - Recommending a course of action.
    - Techniques: Rule-based recommendation engines ("If missing Python and targeting Data Science -> Recommend Python Course").

---

## 7. Machine Learning Model Explanation

### 1. Natural Language Processing (NLP) for Skill Extraction
- **Technique:** Keyword Matching / Named Entity Recognition (NER).
- **Library:** spaCy.
- **Logic:** Iterate through tokens in the job description using a pattern matcher to find known technologies (e.g., 'Python', 'Java', 'SQL').

### 2. Salary Prediction (Regression)
- **Model:** Linear Regression / Random Forest Regressor.
- **Input Features:** Experience (years), Number of Skills, Location (encoded), Job Role (encoded).
- **Target Variable:** Salary.
- **Logic:** Learn the relationship between experience/skills and offered salary to predict a fair salary for the user.

### 3. Demand Forecasting (Time Series)
- **Model:** Linear Regression (Trend Line) or Moving Average.
- **Input:** Time (Months/Years).
- **Target:** Count of Job Postings for a specific skill.
- **Logic:** $y = mx + c$, where $y$ is skill demand and $x$ is time. Positive slope $m$ indicates a growing trend.
