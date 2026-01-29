"""
Streamlit Dashboard for Resume Evaluation System
Placement Team Interface
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Evaluation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:5000/api"

# Helper functions
@st.cache_data
def fetch_data(endpoint):
    """Fetch data from API with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def post_data(endpoint, data):
    """Post data to API"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def upload_file(endpoint, file, form_data):
    """Upload file to API"""
    try:
        files = {'file': file}
        response = requests.post(f"{API_BASE_URL}{endpoint}", files=files, data=form_data)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

# Main Dashboard
def main():
    st.title("🎯 Automated Resume Relevance Check System")
    st.markdown("---")
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Job Management", "Resume Management", "Evaluations", "Upload Files"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Job Management":
        show_job_management()
    elif page == "Resume Management":
        show_resume_management()
    elif page == "Evaluations":
        show_evaluations()
    elif page == "Upload Files":
        show_upload_files()

def show_dashboard():
    """Main dashboard with statistics and charts"""
    st.header("📊 Dashboard Overview")
    
    # Fetch dashboard stats
    stats_data = fetch_data("/dashboard/stats")
    
    if stats_data and stats_data.get('success'):
        stats = stats_data['stats']
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Jobs", stats['total_jobs'])
        
        with col2:
            st.metric("Total Resumes", stats['total_resumes'])
        
        with col3:
            st.metric("Total Evaluations", stats['total_evaluations'])
        
        with col4:
            high_fit = stats['evaluation_distribution']['high_fit']
            total_eval = stats['total_evaluations']
            success_rate = (high_fit / total_eval * 100) if total_eval > 0 else 0
            st.metric("High Fit Rate", f"{success_rate:.1f}%")
        
        st.markdown("---")
        
        # Evaluation Distribution Chart
        col1, col2 = st.columns(2)
        
        with col1:
            eval_dist = stats['evaluation_distribution']
            fig_pie = px.pie(
                values=[eval_dist['high_fit'], eval_dist['medium_fit'], eval_dist['low_fit']],
                names=['High Fit', 'Medium Fit', 'Low Fit'],
                title="Evaluation Distribution",
                color_discrete_map={'High Fit': '#2E8B57', 'Medium Fit': '#FFD700', 'Low Fit': '#DC143C'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Recent Activity
            st.subheader("Recent Evaluations")
            recent_evaluations = stats['recent_evaluations']
            
            if recent_evaluations:
                for eval_data in recent_evaluations[:5]:
                    score = eval_data['relevance_score']
                    verdict = eval_data['verdict']
                    color = "#2E8B57" if verdict == "High" else "#FFD700" if verdict == "Medium" else "#DC143C"
                    
                    st.markdown(f"""
                    <div style="border-left: 4px solid {color}; padding: 10px; margin: 5px 0;">
                        <strong>Score: {score}</strong> | <strong>Verdict: {verdict}</strong><br>
                        <small>Resume ID: {eval_data['resume_id'][:8]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent evaluations found")
    
    else:
        st.error("Unable to load dashboard data")

def show_job_management():
    """Job management interface"""
    st.header("💼 Job Management")
    
    # Create new job
    with st.expander("Create New Job Posting", expanded=True):
        with st.form("create_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
                company = st.text_input("Company", placeholder="e.g., Innomatics Research Labs")
                location = st.text_input("Location", placeholder="e.g., Hyderabad, Bangalore")
            
            with col2:
                description = st.text_area(
                    "Job Description", 
                    placeholder="Paste the complete job description here...",
                    height=200
                )
            
            submitted = st.form_submit_button("Create Job Posting")
            
            if submitted:
                if title and company and location and description:
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': description
                    }
                    
                    result = post_data("/jobs", job_data)
                    if result and result.get('success'):
                        st.success("Job created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create job")
                else:
                    st.error("Please fill in all required fields")
    
    st.markdown("---")
    
    # List existing jobs
    st.subheader("Existing Job Postings")
    
    jobs_data = fetch_data("/jobs")
    if jobs_data and jobs_data.get('success'):
        jobs = jobs_data['jobs']
        
        if jobs:
            # Create DataFrame for display
            df = pd.DataFrame(jobs)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display jobs
            for idx, job in enumerate(jobs):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{job['title']}** at {job['company']}")
                        st.markdown(f"📍 {job['location']} | 📅 {job['created_at']}")
                        st.markdown(f"📊 {job['evaluation_count']} evaluations")
                    
                    with col2:
                        if st.button(f"View Details", key=f"view_{idx}"):
                            st.session_state.selected_job = job
                    
                    with col3:
                        if st.button(f"Evaluate All", key=f"eval_{idx}"):
                            # Trigger batch evaluation
                            st.info("Starting batch evaluation...")
                            # This would call the batch evaluation API
                    
                    st.markdown("---")
        else:
            st.info("No job postings found")
    else:
        st.error("Unable to load jobs")

def show_resume_management():
    """Resume management interface"""
    st.header("📄 Resume Management")
    
    # Resume statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Resumes", "Loading...")
    
    with col2:
        st.metric("Processed", "Loading...")
    
    with col3:
        st.metric("Pending", "Loading...")
    
    st.markdown("---")
    
    # Resume list
    st.subheader("Resume List")
    
    resumes_data = fetch_data("/resumes")
    if resumes_data and resumes_data.get('success'):
        resumes = resumes_data['resumes']
        
        if resumes:
            # Create DataFrame
            df = pd.DataFrame(resumes)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display table
            st.dataframe(
                df[['student_name', 'student_email', 'file_type', 'is_processed', 'created_at']],
                use_container_width=True
            )
            
            # Individual resume details
            st.subheader("Resume Details")
            selected_resume = st.selectbox(
                "Select a resume to view details",
                options=resumes,
                format_func=lambda x: f"{x['student_name']} - {x['original_filename']}"
            )
            
            if selected_resume:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Name:** {selected_resume['student_name']}")
                    st.markdown(f"**Email:** {selected_resume['student_email']}")
                    st.markdown(f"**Phone:** {selected_resume['student_phone'] or 'Not provided'}")
                    st.markdown(f"**File Type:** {selected_resume['file_type'].upper()}")
                    st.markdown(f"**Status:** {'✅ Processed' if selected_resume['is_processed'] else '⏳ Pending'}")
                
                with col2:
                    if selected_resume['parsed_data']:
                        st.markdown("**Extracted Skills:**")
                        skills = selected_resume['parsed_data'].get('skills', [])
                        if skills:
                            st.write(", ".join(skills[:10]))  # Show first 10 skills
                        else:
                            st.write("No skills extracted")
                        
                        st.markdown("**Experience:**")
                        experience = selected_resume['parsed_data'].get('experience', [])
                        st.write(f"{len(experience)} positions found")
        else:
            st.info("No resumes found")
    else:
        st.error("Unable to load resumes")

def show_evaluations():
    """Evaluation results interface"""
    st.header("📊 Evaluation Results")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        jobs_data = fetch_data("/jobs")
        job_options = ["All Jobs"] + [job['title'] for job in jobs_data.get('jobs', [])] if jobs_data and jobs_data.get('success') else ["All Jobs"]
        selected_job = st.selectbox("Filter by Job", job_options)
    
    with col2:
        verdict_filter = st.selectbox("Filter by Verdict", ["All", "High", "Medium", "Low"])
    
    with col3:
        min_score = st.slider("Minimum Score", 0, 100, 0)
    
    st.markdown("---")
    
    # Evaluation results
    evaluations_data = fetch_data("/evaluations")
    if evaluations_data and evaluations_data.get('success'):
        evaluations = evaluations_data['evaluations']
        
        if evaluations:
            # Apply filters
            filtered_evaluations = evaluations
            
            if selected_job != "All Jobs":
                filtered_evaluations = [e for e in filtered_evaluations if e.get('job_title') == selected_job]
            
            if verdict_filter != "All":
                filtered_evaluations = [e for e in filtered_evaluations if e['verdict'] == verdict_filter]
            
            filtered_evaluations = [e for e in filtered_evaluations if e['relevance_score'] >= min_score]
            
            # Display results
            st.subheader(f"Evaluation Results ({len(filtered_evaluations)} found)")
            
            for eval_data in filtered_evaluations:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Resume ID:** {eval_data['resume_id'][:8]}...")
                        st.markdown(f"**Job ID:** {eval_data['job_id'][:8]}...")
                    
                    with col2:
                        score = eval_data['relevance_score']
                        color = "#2E8B57" if score >= 80 else "#FFD700" if score >= 60 else "#DC143C"
                        st.markdown(f"<div style='color: {color}; font-size: 24px; font-weight: bold;'>{score}</div>", unsafe_allow_html=True)
                    
                    with col3:
                        verdict = eval_data['verdict']
                        verdict_color = {"High": "#2E8B57", "Medium": "#FFD700", "Low": "#DC143C"}[verdict]
                        st.markdown(f"<div style='color: {verdict_color}; font-weight: bold;'>{verdict}</div>", unsafe_allow_html=True)
                    
                    with col4:
                        if st.button("View Details", key=f"eval_details_{eval_data['id']}"):
                            st.session_state.selected_evaluation = eval_data
                    
                    # Show missing skills if any
                    missing_skills = eval_data.get('missing_skills', [])
                    if missing_skills:
                        st.markdown(f"**Missing Skills:** {', '.join(missing_skills[:5])}")
                    
                    st.markdown("---")
        else:
            st.info("No evaluations found")
    else:
        st.error("Unable to load evaluations")

def show_upload_files():
    """File upload interface"""
    st.header("📤 Upload Files")
    
    # Upload resume
    st.subheader("Upload Resume")
    
    with st.form("upload_resume_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            student_name = st.text_input("Student Name", placeholder="Enter student name")
            student_email = st.text_input("Student Email", placeholder="Enter student email")
            student_phone = st.text_input("Student Phone", placeholder="Enter phone number (optional)")
        
        with col2:
            uploaded_file = st.file_uploader(
                "Choose a resume file",
                type=['pdf', 'docx'],
                help="Upload PDF or DOCX resume file"
            )
        
        submitted = st.form_submit_button("Upload Resume")
        
        if submitted and uploaded_file is not None:
            if student_name and student_email:
                form_data = {
                    'student_name': student_name,
                    'student_email': student_email,
                    'student_phone': student_phone
                }
                
                result = upload_file("/resumes", uploaded_file, form_data)
                if result and result.get('success'):
                    st.success("Resume uploaded successfully!")
                    st.info("Resume is being processed in the background...")
                else:
                    st.error("Failed to upload resume")
            else:
                st.error("Please provide student name and email")
    
    st.markdown("---")
    
    # Upload job description
    st.subheader("Upload Job Description")
    
    with st.form("upload_jd_form"):
        jd_text = st.text_area(
            "Job Description",
            placeholder="Paste the job description here...",
            height=300
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            job_title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
        
        with col2:
            company_name = st.text_input("Company", placeholder="e.g., Innomatics Research Labs")
        
        with col3:
            location = st.text_input("Location", placeholder="e.g., Hyderabad")
        
        submitted = st.form_submit_button("Create Job Posting")
        
        if submitted and jd_text and job_title and company_name and location:
            job_data = {
                'title': job_title,
                'company': company_name,
                'location': location,
                'description': jd_text
            }
            
            result = post_data("/jobs", job_data)
            if result and result.get('success'):
                st.success("Job posting created successfully!")
            else:
                st.error("Failed to create job posting")
        elif submitted:
            st.error("Please fill in all required fields")

if __name__ == "__main__":
    main()
