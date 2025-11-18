import requests
from bs4 import BeautifulSoup
from django.conf import settings
import json
from .gemini_service import GeminiCVAnalyzer

class JobMatcher:
    def __init__(self):
        self.gemini_analyzer = GeminiCVAnalyzer()
        self.job_portals = {
            'indeed': 'https://www.indeed.com/jobs?q={}&l={}',
            'linkedin': 'https://www.linkedin.com/jobs/search/?keywords={}&location={}',
            'naukri': 'https://www.naukri.com/jobs-in-{}-{}',
            'glassdoor': 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={}&locT=C&locId={}'
        }
    
    def find_matching_jobs(self, cv_analysis, location="", job_title="", limit=20):
        """Find jobs matching the CV analysis"""
        if job_title:
            # Use provided job title
            jobs = self._search_jobs(job_title, location, limit)
            job_suggestions = {'job_titles': [job_title]}
        else:
            # Use fallback job suggestions when Gemini is disabled
            if self.gemini_analyzer.enabled:
                job_suggestions = self.gemini_analyzer.find_matching_jobs(cv_analysis, location)
            else:
                job_suggestions = {
                    'job_titles': ['Software Developer', 'Web Developer', 'Python Developer'],
                    'search_keywords': ['python', 'django', 'web development'],
                    'job_portals': ['LinkedIn', 'Indeed', 'Naukri'],
                    'application_tips': ['Customize resume', 'Write cover letter']
                }
            
            jobs = []
            for title in job_suggestions.get('job_titles', ['Software Developer']):
                portal_jobs = self._search_jobs(title, location, limit//len(job_suggestions.get('job_titles', [1])))
                jobs.extend(portal_jobs)
        
        return {
            'jobs': jobs[:limit],
            'search_suggestions': job_suggestions,
            'total_found': len(jobs)
        }
    
    def _search_jobs(self, job_title, location, limit):
        """Search jobs from multiple portals"""
        jobs = []
        
        # Generate real job portal search URLs
        job_title_encoded = job_title.replace(' ', '%20')
        location_encoded = location.replace(' ', '%20') if location else 'remote'
        
        sample_jobs = [
            {
                'title': f'{job_title}',
                'company': 'Tech Corp',
                'location': location or 'Remote',
                'salary': '$60,000 - $80,000',
                'description': f'Looking for experienced {job_title}...',
                'requirements': ['Python', 'Django', 'REST API'],
                'portal': 'Indeed',
                'url': f'https://www.indeed.com/jobs?q={job_title_encoded}&l={location_encoded}',
                'posted_date': '2 days ago',
                'job_type': 'Full-time'
            },
            {
                'title': f'Senior {job_title}',
                'company': 'Innovation Labs',
                'location': location or 'New York',
                'salary': '$80,000 - $100,000',
                'description': f'Senior {job_title} position...',
                'requirements': ['React', 'Node.js', 'AWS'],
                'portal': 'LinkedIn',
                'url': f'https://www.linkedin.com/jobs/search/?keywords={job_title_encoded}&location={location_encoded}',
                'posted_date': '1 day ago',
                'job_type': 'Full-time'
            },
            {
                'title': f'{job_title} Specialist',
                'company': 'Global Solutions',
                'location': location or 'Mumbai',
                'salary': '₹8,00,000 - ₹12,00,000',
                'description': f'Exciting {job_title} opportunity...',
                'requirements': ['Java', 'Spring Boot', 'Microservices'],
                'portal': 'Naukri',
                'url': f'https://www.naukri.com/jobs-in-{location_encoded}-{job_title_encoded}',
                'posted_date': '3 days ago',
                'job_type': 'Full-time'
            },
            {
                'title': f'{job_title} - Entry Level',
                'company': 'StartupXYZ',
                'location': location or 'Bangalore',
                'salary': '₹6,00,000 - ₹9,00,000',
                'description': f'Great opportunity for {job_title}...',
                'requirements': ['JavaScript', 'React', 'Node.js'],
                'portal': 'Glassdoor',
                'url': f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_title_encoded}&locT=C&locId=1',
                'posted_date': '1 week ago',
                'job_type': 'Full-time'
            }
        ]
        
        return sample_jobs[:limit]
    
    def get_application_guide(self, job_data):
        """Get AI-powered application guide for specific job"""
        guide = self.gemini_analyzer.get_application_guide(
            job_data.get('title', ''),
            job_data.get('company', '')
        )
        
        return {
            'guide': guide,
            'portal_specific_tips': self._get_portal_tips(job_data.get('portal', '')),
            'job_url': job_data.get('url', ''),
            'application_checklist': [
                'Customize resume for this role',
                'Write targeted cover letter',
                'Research company background',
                'Prepare for common interview questions',
                'Practice technical skills if required'
            ]
        }
    
    def _get_portal_tips(self, portal):
        """Get portal-specific application tips"""
        tips = {
            'LinkedIn': [
                'Optimize your LinkedIn profile',
                'Connect with employees at the company',
                'Use LinkedIn messaging for follow-ups'
            ],
            'Indeed': [
                'Upload your resume to Indeed',
                'Set up job alerts',
                'Apply within 24-48 hours of posting'
            ],
            'Naukri': [
                'Keep your profile updated',
                'Use relevant keywords',
                'Apply through mobile app for faster response'
            ],
            'Glassdoor': [
                'Read company reviews',
                'Check salary insights',
                'Prepare for company-specific interview questions'
            ]
        }
        return tips.get(portal, ['Follow standard application process'])
    
    def get_job_resources(self, job_title):
        """Get learning resources for job preparation"""
        resources = {
            'courses': [
                {'name': 'Python for Beginners', 'platform': 'Coursera', 'url': '#'},
                {'name': 'Web Development Bootcamp', 'platform': 'Udemy', 'url': '#'}
            ],
            'certifications': [
                {'name': 'AWS Certified Developer', 'provider': 'Amazon', 'url': '#'},
                {'name': 'Google Cloud Professional', 'provider': 'Google', 'url': '#'}
            ],
            'practice_platforms': [
                {'name': 'LeetCode', 'type': 'Coding Practice', 'url': 'https://leetcode.com'},
                {'name': 'HackerRank', 'type': 'Technical Skills', 'url': 'https://hackerrank.com'}
            ],
            'interview_prep': [
                {'name': 'Pramp', 'type': 'Mock Interviews', 'url': 'https://pramp.com'},
                {'name': 'InterviewBit', 'type': 'Technical Prep', 'url': 'https://interviewbit.com'}
            ]
        }
        return resources