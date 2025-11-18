import google.generativeai as genai
from django.conf import settings
import json
import re

class GeminiCVAnalyzer:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.enabled = True
        except Exception as e:
            self.enabled = False
            print(f"Gemini API initialization failed: {e}")
    
    def analyze_cv(self, cv_text, job_description=""):
        if not self.enabled:
            return self._get_fallback_analysis()
            
        try:
            prompt = f"""
            Analyze this CV and provide detailed feedback:
            
            CV Content: {cv_text}
            Job Description: {job_description}
            
            Provide response in JSON format:
            {{
                "ats_score": 85,
                "missing_sections": ["Skills", "Certifications"],
                "improvements": ["Add quantified achievements", "Include relevant keywords"],
                "keyword_suggestions": ["Python", "Machine Learning", "AWS"],
                "optimized_sections": {{
                    "summary": "Optimized professional summary",
                    "experience": "Enhanced experience section",
                    "skills": "Recommended skills section"
                }},
                "job_match_percentage": 75
            }}
            """
            
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return self._get_fallback_analysis()
    
    def generate_optimized_cv(self, cv_text, analysis_data):
        if not self.enabled:
            return self._get_fallback_optimized_cv(cv_text)
            
        try:
            prompt = f"""
            Create an ATS-optimized CV based on this analysis:
            
            Original CV: {cv_text}
            Analysis: {analysis_data}
            
            Generate a complete, professional CV with:
            - ATS-friendly formatting
            - Relevant keywords
            - Quantified achievements
            - Professional summary
            - Skills section
            - Experience with impact metrics
            
            Return only the CV content in plain text format.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini optimization failed: {e}")
            return self._get_fallback_optimized_cv(cv_text)
    
    def _get_fallback_optimized_cv(self, original_cv):
        return f"""
PROFESSIONAL SUMMARY
====================
Experienced professional with strong technical skills and proven track record of delivering results. 
Seeking to leverage expertise in a challenging role that offers growth opportunities.

CORE COMPETENCIES
=================
• Python Programming
• Web Development
• Database Management
• Problem Solving
• Team Collaboration
• Project Management
• Technical Documentation

PROFESSIONAL EXPERIENCE
======================
[Enhanced version of your original experience with quantified achievements]

EDUCATION
=========
[Your educational background]

TECHNICAL SKILLS
===============
• Programming Languages: Python, JavaScript, SQL
• Frameworks: Django, React, Bootstrap
• Databases: MySQL, PostgreSQL, SQLite
• Tools: Git, Docker, AWS
• Methodologies: Agile, Scrum

CERTIFICATIONS
=============
[Relevant certifications]

Note: This is a sample optimized CV. For best results, please configure the Gemini API key.

Original CV Content:
{original_cv[:500]}...
"""
    
    def find_matching_jobs(self, cv_analysis, location=""):
        if not self.enabled:
            return self._parse_job_response("")
            
        try:
            prompt = f"""
            Based on this CV analysis, suggest job search terms and job types:
            
            Analysis: {cv_analysis}
            Location: {location}
            
            Provide JSON response:
            {{
                "job_titles": ["Software Engineer", "Data Analyst"],
                "search_keywords": ["python", "machine learning"],
                "job_portals": ["LinkedIn", "Indeed", "Naukri"],
                "application_tips": ["Customize resume for each job", "Write compelling cover letter"]
            }}
            """
            
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini job matching failed: {e}")
            return self._parse_job_response("")
    
    def get_application_guide(self, job_title, company_name=""):
        if not self.enabled:
            return f"Gemini API not configured. Please add your API key to use AI-powered guidance."
            
        try:
            prompt = f"""
            Provide a comprehensive job application guide for:
            Job Title: {job_title}
            Company: {company_name}
            
            Include:
            1. Application strategy
            2. Interview preparation tips
            3. Common questions
            4. Skills to highlight
            5. Resources for preparation
            
            Format as structured text.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini guide generation failed: {e}")
            return f"Application guide for {job_title} - Please configure Gemini API for detailed guidance."
    
    def _parse_response(self, text):
        # Fallback parser for non-JSON responses
        return {
            "ats_score": 70,
            "missing_sections": ["Skills"],
            "improvements": ["Improve formatting", "Add keywords"],
            "keyword_suggestions": ["Relevant skills"],
            "optimized_sections": {"summary": "Professional summary needed"},
            "job_match_percentage": 65
        }
    
    def _parse_job_response(self, text):
        return {
            "job_titles": ["Software Developer"],
            "search_keywords": ["programming"],
            "job_portals": ["LinkedIn", "Indeed"],
            "application_tips": ["Tailor your resume"]
        }
    
    def _get_fallback_analysis(self):
        return {
            "ats_score": 75,
            "missing_sections": ["Professional Summary", "Skills Section", "Keywords Optimization"],
            "improvements": [
                "Add relevant keywords for your target role",
                "Include quantified achievements in experience",
                "Optimize formatting for ATS compatibility",
                "Add a professional summary section",
                "Include technical skills section"
            ],
            "keyword_suggestions": [
                "Python", "Django", "Web Development", "Problem Solving",
                "Team Collaboration", "Project Management", "Database Management"
            ],
            "optimized_sections": {
                "summary": "Professional summary with key achievements and skills",
                "experience": "Enhanced experience section with quantified results",
                "skills": "Comprehensive skills section with relevant technologies"
            },
            "job_match_percentage": 70
        }