# CareerGraph AI: Industry Skill Intelligence & Interview Readiness

## Overview
This project is a Data Analytics and AI-based system designed to analyze job market trends, identify skill gaps for users, and predict future demands using Machine Learning.

## Structure
- `docs/`: Contains full project documentation (SRS, Methodology, Results).
- `src/`: Python source code for the system.
- `data/`: (Generated) Dataset files.

## How to Run

### Option 1: VS Code (Recommended)
1. Open this folder in VS Code.
2. Install the recommended extensions (Python, Pylance).
3. Press **F5** or go to the **Run and Debug** tab.
4. Select **"Python: Streamlit Dashboard"** to launch the interactive UI.
5. Alternatively, select **"Python: Mock Data Generator"** if you need to regenerate initial data.

### Option 2: Command Line
1. **Setup Environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate # Linux/Mac
   pip install -r requirements.txt
   ```
2. **Launch Dashboard:**
   ```bash
   streamlit run src/dashboard.py
   ```
3. **Run Analysis CLI:**
   ```bash
   python src/main_analysis.py
   ```

## Key Features
- **Industry Insight:** Real-time analysis of job market trends.
- **Skill Gap Analysis:** Personalized reports based on resume uploads.
- **AI Interview Prep:** Virtual interview intelligence with expert feedback.
- **Salary Projection:** ML-based future salary forecasting.
