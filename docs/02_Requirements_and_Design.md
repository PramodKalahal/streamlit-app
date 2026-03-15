# Software Requirements Specification (SRS) & System Design

## 3. Software Requirements Specification (SRS)

### 3.1 Functional Requirements
- **Data Ingestion Module:** The system shall ingest job descriptions and market data from CSV/Excel files (or scraped data).
- **Preprocessing Module:** The system shall clean text data, handle missing values, and perform tokenization/lemmatization using NLP.
- **Skill Extraction:** The system shall extract specific technical and soft skills from unstructured text using Named Entity Recognition (NER).
- **Resume Parsing (Unique Feature):** The system shall allow users to upload PDF resumes to automatically extract and populate their skill profile.
- **User Profiling:** The system shall allow users to input or edit their current skills.
- **Gap Analysis:** The system shall calculate the difference between user skills and target job requirements.
- **Course Recommendation (Unique Feature):** The system shall provide specific course links (e.g., Coursera, Udemy) for identified skill gaps.
- **Forecasting:** The system shall predict future demand for top skills using historical trend data.
- **Reporting:** The system shall generate visual reports (Bar charts, Line graphs, Heatmaps).

### 3.2 Non-Functional Requirements
- **Performance:** Data processing should complete within reasonable time limits for datasets up to 100,000 records.
- **Scalability:** The architecture should support adding new data sources.
- **Accuracy:** Skill extraction should have a precision of at least 80%.
- **Usability:** The command-line interface or dashboard charts should be clear and distinct.

### 3.3 Hardware & Software Requirements
- **OS:** Windows 10/11, Linux, or macOS.
- **Language:** Python 3.8+
- **Database:** MySQL (8.0+)
- **Libraries:** Pandas, NumPy, Scikit-learn, SpaCy, Matplotlib/Seaborn.
- **IDE:** VS Code / Jupyter Notebook.

---

## 4. System Architecture Diagram

*(Textual Representation)*

```text
[ Data Sources ]       [ User Input ]
(Job Portals, csv)     (Resume/Skills)
       |                     |
       v                     v
[ Data Ingestion & Preprocessing Layer ]
(Cleaning, Normalization, Tokenization - NLP)
       |                     |
       v                     v
      [ Core Analytics Engine ]
      /           |            \
     /            |             \
[Descriptive] [Diagnostic]   [Predictive]
(Trend Analysis)(Gap Analysis) (Forecasting - ML)
     |            |              |
     v            v              v
      [ Presentation Layer / Dashboard ]
      (Power BI / Python Visualizations)
                  |
                  v
           [ End User ]
```

---

## 8. Dataset Description

The system uses a dataset representing job market listings. 

**Attributes:**
1.  **Job_ID:** Unique identifier for the job posting.
2.  **Job_Title:** Title of the role (e.g., "Data Scientist", "Python Developer").
3.  **Company:** Name of the hiring company.
4.  **Location:** Job location.
5.  **Salary_Range:** Annual compensation offered.
6.  **Job_Description:** Full text description of the job.
7.  **Date_Posted:** Date the job was advertised.
8.  **Skills_Required:** (Extracted) List of skills mentioned.
9.  **Experience_Level:** Entry, Mid, Senior.
