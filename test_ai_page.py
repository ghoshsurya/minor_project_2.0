#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ats_optimizer.settings')
django.setup()

from django.contrib.auth import get_user_model
from cv_optimizer.models import CVUpload
from cv_optimizer.gemini_service import GeminiCVAnalyzer

def test_ai_page():
    User = get_user_model()
    
    # Create test user if doesn't exist
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Create test CV upload
    cv_upload, created = CVUpload.objects.get_or_create(
        user=user,
        job_role='Software Developer',
        defaults={
            'ats_score': 75.0,
            'gemini_analysis': {
                'ats_score': 75,
                'missing_sections': ['Skills', 'Certifications'],
                'improvements': ['Add keywords', 'Improve formatting'],
                'keyword_suggestions': ['Python', 'Django', 'JavaScript'],
                'job_match_percentage': 80
            },
            'missing_sections': ['Skills', 'Certifications'],
            'improvement_suggestions': ['Add keywords', 'Improve formatting'],
            'keyword_suggestions': ['Python', 'Django', 'JavaScript'],
            'job_match_percentage': 80.0,
            'optimized_content': 'Sample optimized CV content for testing'
        }
    )
    
    print(f"Test CV created with ID: {cv_upload.id}")
    print(f"Test URL: http://127.0.0.1:8000/cv/ai-optimized/{cv_upload.id}/")
    
    # Test Gemini service
    analyzer = GeminiCVAnalyzer()
    print(f"Gemini API enabled: {analyzer.enabled}")
    
    if not analyzer.enabled:
        print("Gemini API not configured - using fallback data")
        fallback = analyzer._get_fallback_analysis()
        print(f"Fallback ATS Score: {fallback['ats_score']}")

if __name__ == '__main__':
    test_ai_page()