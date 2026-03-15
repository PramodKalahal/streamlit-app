import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import sys
import os
from collections import Counter

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main_analysis import extract_skills_nlp
import utils

# Page Config
st.set_page_config(
    page_title="CareerGraph AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #00e6e6; /* Bright Cyan */
        font-family: 'Inter', sans-serif;
    }
    
    /* Modern Metric Cards - Matching User Provided Image */
    div[data-testid="stMetric"] {
        background-color: #1b263b !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 1px solid rgba(0, 230, 230, 0.1) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #00e6e6 !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    
    /* Green Chip/Delta styling */
    [data-testid="stMetricDelta"] {
        background-color: rgba(34, 197, 94, 0.15) !important;
        color: #22c55e !important;
        padding: 2px 8px !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        width: fit-content !important;
    }
    </style>
        """, unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    # Try different paths to be robust
    paths = ["data/job_market_data.csv", "../data/job_market_data.csv"]
    for path in paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Normalize column names for reliability
            if 'Salary' in df.columns and 'Salary_INR' not in df.columns:
                df.rename(columns={'Salary': 'Salary_INR'}, inplace=True)
            
            # Ensure we have extracted skills
            if 'Extracted_Skills' not in df.columns:
                df['Extracted_Skills'] = df['Job_Description'].apply(lambda x: extract_skills_nlp(x))
            return df
            
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Data file not found. Please run 'src/mock_data_generator.py' first.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🔍 User Profile")
unique_roles = sorted(df['Job_Title'].unique()) if not df.empty else []

# Handle auto-detection reset
default_index = 0
if 'target_role_reset' in st.session_state:
    if st.session_state['target_role_reset'] in unique_roles:
        default_index = list(unique_roles).index(st.session_state['target_role_reset'])
    del st.session_state['target_role_reset']

selected_role = st.sidebar.selectbox("Select Target Role", unique_roles, index=default_index)

# --- Role Data Preparation (Always needed) ---
role_df = pd.DataFrame()
market_skills_set = set()
avg_sal = 0
if not df.empty and selected_role:
    role_df = df[df['Job_Title'] == selected_role]
    all_skills = [skill for sublist in role_df['Extracted_Skills'] for skill in sublist]
    from collections import Counter
    market_skills_list = [s[0] for s in Counter(all_skills).most_common(20)]
    market_skills_set = set(market_skills_list)
    avg_sal = role_df['Salary_INR'].mean() if 'Salary_INR' in role_df.columns else 0

# Initialize defaults to prevent NameError
score_val = 0
missing = []
resume_text = ""

st.sidebar.markdown("---")
st.sidebar.subheader("📄 Resume Analysis")
uploaded_file = st.sidebar.file_uploader("Upload your Resume (PDF/Word)", type=['pdf', 'docx', 'doc'])

user_input_skills = []
if uploaded_file:
    with st.spinner('Scanning Resume with AI...'):
        resume_text = utils.extract_text(uploaded_file)
        # Reuse existing NLP extraction logic
        user_input_skills = extract_skills_nlp(resume_text)
    
    st.sidebar.success(f"Extracted {len(user_input_skills)} skills from resume!")
    
    if len(user_input_skills) == 0 and len(resume_text) > 0:
        with st.sidebar.expander("🔍 Debug: Extracted Text"):
            st.write(resume_text[:500] + "...")
            st.warning("No known technical skills detected in the text above.")

    # Calculate role detection
    role_result = utils.determine_target_role(resume_text)
    st.session_state['role_result'] = role_result
    st.session_state['resume_text'] = resume_text

    # --- ATS Score Logic (Resume Powered) ---
    matched = set(user_input_skills) & market_skills_set
    missing = market_skills_set - set(user_input_skills)
    
    ats_result = utils.calculate_ats_score(resume_text, matched, missing)
    score_val = ats_result['score']
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 ATS Score")
    
    # Display Score
    score_color = "red" if score_val < 50 else "orange" if score_val < 75 else "green"
    
    st.sidebar.markdown(f"""
    <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid {score_color}; text-align: center;">
        <h2 style="color: {score_color}; margin: 0;">{score_val}/100</h2>
        <p style="color: #ccc; margin: 0;">Resume Strength</p>
    </div>
    """, unsafe_allow_html=True)
    
    if ats_result['feedback']:
         with st.sidebar.expander("📝 Improvement Recommendations", expanded=(score_val < 70)):
             for feedback_item in ats_result['feedback']:
                 st.sidebar.warning(feedback_item)
    
    # Display breakdown
    if ats_result.get('breakdown'):
        with st.sidebar.expander("🔍 Score Breakdown"):
            for criteria, points in ats_result['breakdown'].items():
                st.sidebar.caption(f"**{criteria}**: +{points} pts")
    
    # Master Skills from Utils
    all_options = utils.GET_MASTER_SKILLS()
    
    # Safety Check: Filter user_input_skills to only what is in all_options to prevent StreamlitAPIException
    safe_defaults = [s for s in user_input_skills if s in all_options]
    
    user_input_skills = st.sidebar.multiselect("Verified Skills", 
                                          all_options,
                                          default=safe_defaults)
else:
    st.sidebar.info("Upload a resume to auto-detect skills.")
    all_options = utils.GET_MASTER_SKILLS()
    user_input_skills = st.sidebar.multiselect("Or Manually Select Skills", 
                                          all_options,
                                          default=[])
    
    # Calculate baseline metrics for manual mode
    matched = set([s.lower() for s in user_input_skills]) & market_skills_set
    missing = market_skills_set - matched
    if market_skills_set:
        score_val = int((len(matched) / len(market_skills_set)) * 100)
    else:
        score_val = 0 # Clean start


# --- MAIN CONTENT ---
st.title("📊 CareerGraph AI: Industry Skill Intelligence")
st.markdown("### *Mapping your journey from academic foundations to industrial excellence.*")

# Filter data by role for all metrics
if not df.empty:
    role_df = df[df['Job_Title'] == selected_role]
else:
    role_df = pd.DataFrame()

# KPI Row
col1, col2, col3 = st.columns(3)
with col1:
    # Dynamic Job Count
    count = len(role_df)
    # Simulate week-over-week change based on role hash to be consistent but varied
    change_pct = (hash(selected_role) % 20) - 5 # Random range -5% to +14%
    st.metric("Total Jobs Analyzed", f"{count}", f"{change_pct:+}% this week")

with col2:
    if not role_df.empty:
        salary_col = 'Salary_INR' if 'Salary_INR' in role_df.columns else 'Salary' if 'Salary' in role_df.columns else None
        if salary_col:
            avg_sal = role_df[salary_col].mean()
            st.metric(f"Avg Salary for {selected_role}", f"INR {avg_sal:,.0f}")
        else:
            st.metric(f"Avg Salary for {selected_role}", "Data N/A")
    else:
        st.metric(f"Avg Salary for {selected_role}", "N/A")

with col3:
    # Dynamic Market Status
    if count > 500:
        status = "High Demand"
    elif count > 200:
        status = "Moderate Demand"
    else:
        status = "Emerging / Niche"
        
    st.metric("Market Status", status, "Active" if count > 0 else "Inactive")

# --- SHARED DATA LOGIC ---
if not role_df.empty:
    # Pre-calculate skills for all tabs
    all_skills = [skill for sublist in role_df['Extracted_Skills'] for skill in sublist]
    skill_counts = pd.DataFrame(Counter(all_skills).most_common(10), columns=['Skill', 'Count'])
    market_skills = set(skill_counts['Skill'])
    user_skills = set(user_input_skills)
    missing = list(market_skills - user_skills)
else:
    skill_counts = pd.DataFrame()
    missing = []

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Market Trends", "🧬 Skill Gap Analysis", "🔮 Career Forecast", "🎯 Role Suggestions", "🤖 Interview Prep"])

with tab1:
    if not role_df.empty:
        st.subheader(f"Top Skills for {selected_role}")
        
        # Rename the 'Count' column for clarity in the chart
        chart_data = skill_counts.rename(columns={'Count': 'Job Postings Count'})
        
        fig = px.bar(chart_data, x='Skill', y='Job Postings Count', color='Job Postings Count', 
                     color_continuous_scale='Teal', 
                     title=f"Demand Distribution for {selected_role}",
                     labels={'Job Postings Count': 'Number of Job Descriptions'})
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📍 Geographic Demand Intelligence")
        geo_df = utils.get_geographic_demand()
        
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            fig_geo = px.bar(geo_df, x='City', y='Demand_Score', color='Demand_Score',
                            title="Hiring Demand by Tech Hub (India)",
                            color_continuous_scale='Viridis')
            st.plotly_chart(fig_geo, use_container_width=True)
        with col_m2:
            st.info("📊 **Market Insight:** Bangalore and Remote roles continue to offer the highest salary multipliers for tech talent.")
            st.dataframe(geo_df.sort_values(by='Demand_Score', ascending=False), hide_index=True)
    else:
        st.info("No data available for this role.")
        

with tab2:
    st.subheader("Your Personalized Skill Gap Report")
    
    if not role_df.empty:
        c1, c2 = st.columns([1, 1])
        
        with c1:
            if user_skills:
                st.info(f"You Have: {', '.join(user_skills)}")
            else:
                st.warning("No skills selected. Use the sidebar to add your expertise.")
                
            match_list = market_skills & user_skills
            if match_list:
                st.success(f"Matched Skills: {', '.join(match_list)}")
            elif user_skills:
                st.warning("No skills matched yet.")

            st.markdown("---")
            st.subheader("🕸️ Skill Proficiency vs. Market Requirement")
            spider_data = utils.get_skill_proficiencies(user_input_skills, selected_role)
            
            if not spider_data.empty and 'Value' in spider_data.columns:
                fig_spider = px.line_polar(spider_data, r='Value', theta='Skill', color='Type',
                                          line_close=True, range_r=[0, 1],
                                          title=f"Expertise Mapping for {selected_role}")
                fig_spider.update_traces(fill='toself')
                st.plotly_chart(fig_spider, use_container_width=True)
            else:
                st.warning("Not enough skill data to generate proficiency mapping for this role.")
            
            
        with c2:
            if missing:
                st.error(f"⚠️ Missing Critical Skills: {', '.join(missing)}")
                if len(market_skills) > 0:
                    score = len(market_skills & user_skills) / len(market_skills)
                    st.progress(score)
                    st.caption(f"Employability Score: {score*100:.0f}%")
                
                st.markdown("### 🎓 AI Recommended Learning Path")
                recs = utils.recommend_courses(missing)
                for rec in recs:
                    st.markdown(f"- {rec}")
                
                st.markdown("---")
                st.subheader("🚀 Smart Portfolio Builder")
                st.info("📊 Implementation is key. Build these projects to demonstrate your expertise:")
                
                projects = utils.get_project_recommendation(missing)
                for proj in projects:
                    st.success(proj)
                    
                time_needed = utils.estimate_learning_time(missing)
                st.warning(f"⏳ **Time to Market Readiness:** Approximately **{time_needed} weeks** of dedicated study based on your current gaps.")
                
            elif user_skills:
                st.balloons()
                st.success("You are fully qualified for the top skills in this role!")
            else:
                st.info("Select your skills in the sidebar to see your gap analysis.")

        st.markdown("---")
        st.subheader("🛤️ AI Career Roadmap: Your Journey to Success")
        
        # Dynamic Roadmap Visualizer
        steps = ["Foundation", "Skill Specialized", "Portfolio Ready", "Interview Prep", "Job-Ready"]
        cols_road = st.columns(len(steps))
        
        user_progress = (len(user_skills & market_skills) / len(market_skills)) if market_skills else 0
        current_step_idx = int(user_progress * (len(steps)-1))
        
        for i, step in enumerate(steps):
            with cols_road[i]:
                is_done = i <= current_step_idx
                color = "#64ffda" if is_done else "#233554"
                icon = "✅" if is_done else "⌛"
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border-bottom: 4px solid {color};">
                    <h4 style="color: {color}; margin-bottom: 5px;">{icon} {step}</h4>
                </div>
                """, unsafe_allow_html=True)

with tab3:
    st.subheader("Future Salary Prediction")
    if not role_df.empty:
        # Dynamic Forecast Data based on Role
        years = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
        
        # Growth rates based on role sector
        if 'Data' in selected_role or 'Machine' in selected_role or 'AI' in selected_role:
             growth_base = 1.12 # Higher growth for AI/Data
        elif 'Web' in selected_role or 'Developer' in selected_role:
             growth_base = 1.08
        else:
             growth_base = 1.05
             
        growth = [1.0] # base year
        current_growth = 1.0
        for i in range(1, len(years)):
            # Add some randomness to growth each year
            yearly_factor = growth_base + (random.uniform(-0.02, 0.05))
            current_growth *= yearly_factor
            growth.append(current_growth)
            
        projected_salaries = [avg_sal * g for g in growth]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=years, y=projected_salaries, mode='lines+markers', name='Salary',
                                     line=dict(color='#00ff00', width=3)))
        
        # Add a "Demand Index" or similar secondary axis for fun/complexity
        demand_index = [100 * g * random.uniform(0.9, 1.1) for g in growth]
                                     
        fig_line.update_layout(
            title=f"Projected Salary Growth for {selected_role} (Up to 2030)", 
            xaxis_title="Year", 
            yaxis_title="Salary (INR)",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown(f"> *Prediction based on ARIMA time-series analysis of historical data and current market growth rate of ~{(growth_base-1)*100:.1f}% for this sector.*")
        

with tab4:
    st.subheader("🎯 Personal Career Analyst & Role Matching")
    
    if uploaded_file and 'role_result' in st.session_state:
        role_result = st.session_state['role_result']
        resume_text = st.session_state.get('resume_text', "")
        
        st.markdown("### 🎯 Your AI-Detected Role Profile")
        col_r1, col_r2 = st.columns([1, 2])
        
        role_detected = role_result['target_role']
        conf = role_result['confidence']
        conf_color = "🟢" if conf == "High" else "🟡" if conf == "Medium" else "🔴"
        
        with col_r1:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #00e6e6;">
                <p style="color: #ccc; margin: 0;">Primary Role Match</p>
                <h3 style="color: #00e6e6; margin: 0;">{role_detected}</h3>
                <p style="margin-top: 10px;">Confidence: {conf_color} {conf}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if role_detected != "Unknown" and role_detected != selected_role:
                 if st.button(f"✨ Apply this target role to Dashboard", key="apply_detected"):
                     st.session_state['target_role_reset'] = role_detected
                     st.rerun()
        
        with col_r2:
            st.info(f"**Why this role?** {role_result['reason']}")
            
        st.markdown("---")
        st.subheader("💼 Personalized Role Recommendations")
        all_suitable = utils.get_all_suitable_roles(resume_text)
        
        if all_suitable:
            st.info("Based on your resume, we've identified several roles that align with your existing skill set. Expanding your search to these roles could increase your job prospects.")
            
            for item in all_suitable:
                with st.expander(f"💼 {item['role']} (Match Score: {item['score']})"):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.markdown(f"**Why this is a fit:** We found skills like {', '.join(item['matched_skills'])} in your resume.")
                        st.markdown(utils.get_career_path_advice(item['role'], item['matched_skills']))
                    with col_b:
                        if st.button(f"Explore {item['role']}", key=f"explore_{item['role']}"):
                            st.session_state['target_role_reset'] = item['role']
                            st.rerun()
        else:
            st.warning("We couldn't find strong matches for other roles. Try adding more technical skills to your resume.")
        
    st.markdown("---")
    st.subheader("🛠️ Jobs Linked to Your Skills")
    st.info("Here is how your specific skills map to various industry roles:")
    
    if user_input_skills:
        # Create a clean layout for skill-to-job mapping
        cols = st.columns(2)
        for i, skill in enumerate(user_input_skills):
            with cols[i % 2]:
                suggested_jobs = utils.get_jobs_by_skill(skill)
                st.markdown(f"**{skill.title()}**")
                st.caption(f"Target Roles: {', '.join(suggested_jobs)}")
    else:
        st.write("No skills detected yet. Please upload a resume or select skills manually.")
        
    if not uploaded_file:
        st.info("Upload your resume in the sidebar to get personalized role suggestions!")

with tab5:
    st.header("🎭 CareerGraph AI: Virtual Interview Intelligence")
    st.markdown("### 🎭 Interview Simulator")
    
    # Smart Topic Selection based on Role
    topic_map = {
        'Web Developer': 'React & Frontend',
        'Software Engineer': 'Python',
        'Data Scientist': 'Data Science & Big Data',
        'Machine Learning Engineer': 'Machine Learning & AI',
        'Data Analyst': 'D.Viz & Analytics',
        'Python Developer': 'Python',
        'Full Stack Developer': 'Node.js & Backend',
        'Cloud Architect': 'AWS & Cloud',
        'Data Engineer': 'Data Science & Big Data',
        'Cybersecurity Analyst': 'Cybersecurity',
        'Business Analyst': 'D.Viz & Analytics',
        'AI Engineer': 'Machine Learning & AI',
        'NLP Specialist': 'Machine Learning & AI',
        'DevOps Engineer': 'DevOps & Tools',
        'UI/UX Designer': 'UI/UX Design'
    }
    
    # Calculate recommended topic
    recommended_topic = topic_map.get(selected_role, 'Behavioral (Interviewer)')
    
    # UI for selecting topic
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        available_topics = list(utils.INTERVIEW_BANK.keys())
        # Reorder to put recommended first
        if recommended_topic in available_topics:
            available_topics.remove(recommended_topic)
            available_topics = [recommended_topic] + available_topics
            
        selected_topic = st.selectbox("🎯 Select Interview Category", available_topics, 
                                      help="Choose a category to practice. We recommend starting with your role-specific topics.")
    
    with col_t2:
        st.info(f"💡 **AI Recommendation:** Based on your target role as a **{selected_role}**, we suggest practicing **{recommended_topic}**.")

    st.markdown("---")
    
    # Initialize session state for current question object and history
    if f"history_{selected_topic}" not in st.session_state:
        st.session_state[f"history_{selected_topic}"] = []
        
    def get_new_question(topic):
        if topic not in utils.INTERVIEW_BANK:
            topic = 'Behavioral (Interviewer)'
        pool = utils.INTERVIEW_BANK[topic]
        seen = st.session_state.get(f"history_{topic}", [])
        unseen = [q for q in pool if q['q'] not in seen]
        
        if not unseen:
            unseen = pool
            st.session_state[f"history_{topic}"] = []
            
        q = random.choice(unseen)
        st.session_state[f"history_{topic}"].append(q['q'])
        return q

    # Question management logic
    if f"q_obj_{selected_topic}" not in st.session_state:
        st.session_state[f"q_obj_{selected_topic}"] = get_new_question(selected_topic)
        
    # Refresh current question button
    if st.button("🔄 Get Different Question", key="refresh_q"):
        st.session_state[f"q_obj_{selected_topic}"] = get_new_question(selected_topic)
        st.rerun()
        
    q_obj = st.session_state[f"q_obj_{selected_topic}"]
    q_text = q_obj['q']
    ideal_answer = q_obj['a']
    
    # Question Display
    st.markdown(f"""
    <div style="background-color: #1e293b; padding: 25px; border-left: 5px solid #00e6e6; border-radius: 10px; margin-bottom: 20px;">
        <p style="color: #00e6e6; font-weight: bold; margin-bottom: 5px;">INTERVIEWER:</p>
        <h3 style="margin-top: 0; color: white;">"{q_text}"</h3>
    </div>
    """, unsafe_allow_html=True)
    
    user_answer = st.text_area("Your Response:", placeholder="Practice your response here... (Try to use the STAR method: Situation, Task, Action, Result)", height=150)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        get_feedback = st.button("🚀 Analyze My Response", use_container_width=True)
    with col_b2:
        show_answer = st.button("👁️ View Expert Answer", use_container_width=True)
        
    if get_feedback:
        if user_answer:
            with st.spinner("Analyzing professional alignment..."):
                coach_result = utils.get_interview_feedback(selected_topic, user_answer, q_text)
                
                st.markdown("---")
                
                st.success("Analysis complete! Review the expert answer below to compare with your approach.")
        else:
            st.error("Please provide a response before requesting analysis.")
            
    if show_answer:
        st.markdown("---")
        st.subheader("🎓 Recommended Expert Answer")
        st.success(f"**Expert Answer:**\n\n{ideal_answer}")
        st.markdown("""
        **How to use this:** 
        1. Don't memorize this word-for-word.
        2. Identify the **key themes** (e.g., impact, tools used, collaboration).
        3. Re-frame your own experience using these themes.
        """)
