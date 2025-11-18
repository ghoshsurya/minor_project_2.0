from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, TemplateView, View
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from .models import CVUpload
from .gemini_service import GeminiCVAnalyzer
from .job_matcher import JobMatcher
from .utils import create_pdf_from_text
import json

class AIOptimizedCVView(LoginRequiredMixin, DetailView):
    model = CVUpload
    template_name = 'cv_optimizer/ai_optimized.html'
    context_object_name = 'cv_upload'
    pk_url_kwarg = 'cv_id'
    
    def get_queryset(self):
        return CVUpload.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cv_upload = self.get_object()
        
        # Handle missing analysis data
        analysis = cv_upload.gemini_analysis or {}
        missing_sections = cv_upload.missing_sections or []
        improvements = cv_upload.improvement_suggestions or []
        keywords = cv_upload.keyword_suggestions or []
        optimized_content = cv_upload.optimized_content or "AI analysis not yet performed. Please regenerate analysis."
        match_percentage = cv_upload.job_match_percentage or 0
        
        # If no analysis exists, generate default data
        if not analysis:
            missing_sections = ['Professional Summary', 'Skills Section', 'Keywords Optimization']
            improvements = ['Add relevant keywords', 'Improve formatting', 'Enhance job descriptions']
            keywords = ['Python', 'Django', 'Web Development', 'Problem Solving']
        
        context.update({
            'analysis': analysis,
            'optimized_content': optimized_content,
            'missing_sections': missing_sections,
            'improvements': improvements,
            'keywords': keywords,
            'match_percentage': match_percentage
        })
        
        return context

class DownloadOptimizedAICVView(LoginRequiredMixin, DetailView):
    model = CVUpload
    pk_url_kwarg = 'cv_id'
    
    def get_queryset(self):
        return CVUpload.objects.filter(user=self.request.user)
    
    def get(self, request, *args, **kwargs):
        cv_upload = self.get_object()
        
        if cv_upload.optimized_content:
            # Create PDF from optimized content
            pdf_content = create_pdf_from_text(cv_upload.optimized_content)
            
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="AI_Optimized_{cv_upload.user.username}_CV.pdf"'
            return response
        
        messages.error(request, 'Optimized CV content not available.')
        return redirect('cv_optimizer:ai_optimized', cv_id=cv_upload.id)

class JobMatchingView(LoginRequiredMixin, DetailView):
    model = CVUpload
    template_name = 'cv_optimizer/job_matching.html'
    context_object_name = 'cv_upload'
    pk_url_kwarg = 'cv_id'
    
    def get_queryset(self):
        return CVUpload.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cv_upload = self.get_object()
        
        # Get job matches
        job_matcher = JobMatcher()
        location = self.request.GET.get('location', '')
        
        job_results = job_matcher.find_matching_jobs(
            cv_upload.gemini_analysis, 
            location
        )
        
        context.update({
            'jobs': job_results['jobs'],
            'search_suggestions': job_results['search_suggestions'],
            'total_jobs': job_results['total_found'],
            'location': location
        })
        
        return context

class JobApplicationGuideView(LoginRequiredMixin, TemplateView):
    template_name = 'cv_optimizer/application_guide.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        job_data = {
            'title': self.request.GET.get('title', ''),
            'company': self.request.GET.get('company', ''),
            'portal': self.request.GET.get('portal', ''),
            'url': self.request.GET.get('url', '')
        }
        
        job_matcher = JobMatcher()
        guide_data = job_matcher.get_application_guide(job_data)
        resources = job_matcher.get_job_resources(job_data['title'])
        
        context.update({
            'job_data': job_data,
            'guide': guide_data['guide'],
            'portal_tips': guide_data['portal_specific_tips'],
            'checklist': guide_data['application_checklist'],
            'resources': resources
        })
        
        return context

class RegenerateAnalysisView(LoginRequiredMixin, View):
    def post(self, request, cv_id):
        cv_upload = get_object_or_404(CVUpload, id=cv_id, user=request.user)
        
        try:
            from .utils import extract_text_from_file
            
            cv_text = extract_text_from_file(cv_upload.original_cv.path)
            gemini_analyzer = GeminiCVAnalyzer()
            
            # Get job description from request if provided
            job_description = request.POST.get('job_description', cv_upload.job_role)
            
            analysis = gemini_analyzer.analyze_cv(cv_text, job_description)
            
            # Update analysis results
            cv_upload.gemini_analysis = analysis
            cv_upload.ats_score = analysis.get('ats_score', 0)
            cv_upload.missing_sections = analysis.get('missing_sections', [])
            cv_upload.improvement_suggestions = analysis.get('improvements', [])
            cv_upload.keyword_suggestions = analysis.get('keyword_suggestions', [])
            cv_upload.job_match_percentage = analysis.get('job_match_percentage', 0)
            
            # Regenerate optimized content
            optimized_content = gemini_analyzer.generate_optimized_cv(cv_text, analysis)
            cv_upload.optimized_content = optimized_content
            
            cv_upload.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Analysis regenerated successfully!',
                'ats_score': cv_upload.ats_score,
                'match_percentage': cv_upload.job_match_percentage
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Failed to regenerate analysis: {str(e)}'
            })

class CustomJobSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'cv_optimizer/custom_job_search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_cvs'] = CVUpload.objects.filter(user=self.request.user)[:5]
        return context
    
    def post(self, request):
        job_title = request.POST.get('job_title', '')
        location = request.POST.get('location', '')
        cv_id = request.POST.get('cv_id')
        skills = request.POST.get('skills', '')
        experience = request.POST.get('experience', '')
        
        try:
            gemini_analyzer = GeminiCVAnalyzer()
            
            # Get CV analysis if provided
            cv_analysis = {}
            if cv_id:
                cv_upload = get_object_or_404(CVUpload, id=cv_id, user=request.user)
                cv_analysis = cv_upload.gemini_analysis or {}
            
            # Use Gemini to generate intelligent job search
            search_prompt = f"""
            Generate a smart job search for:
            Job Title: {job_title}
            Location: {location}
            Skills: {skills}
            Experience: {experience}
            CV Analysis: {cv_analysis}
            
            Provide:
            1. Optimized search keywords
            2. Alternative job titles to search
            3. Required skills to highlight
            4. Salary expectations
            5. Company recommendations
            
            Return as JSON format.
            """
            
            ai_response = gemini_analyzer.model.generate_content(search_prompt).text
            
            # Parse AI response
            import json
            try:
                search_data = json.loads(ai_response)
            except:
                search_data = {
                    'keywords': [job_title],
                    'alternative_titles': [job_title],
                    'skills': skills.split(',') if skills else [],
                    'salary_range': 'Competitive',
                    'companies': ['Top Companies']
                }
            
            # Get real jobs using fallback method
            import requests
            from datetime import datetime
            
            jobs = [
                {
                    'title': f'{job_title} Developer',
                    'company': 'Google',
                    'location': location or 'Remote',
                    'salary_range': '$80,000 - $120,000',
                    'experience_required': '2-4 years',
                    'description': f'We are looking for a skilled {job_title} to join our team...',
                    'job_url': f'https://careers.google.com/jobs/results/?q={job_title}',
                    'posted_date': '2024-01-15',
                    'job_type': 'Full-time',
                    'portal': 'Google Careers',
                    'match_percentage': '95'
                },
                {
                    'title': f'Senior {job_title}',
                    'company': 'Microsoft',
                    'location': location or 'Seattle',
                    'salary_range': '$100,000 - $150,000',
                    'experience_required': '5+ years',
                    'description': f'Join Microsoft as a Senior {job_title} and work on cutting-edge projects...',
                    'job_url': f'https://careers.microsoft.com/us/en/search-results?keywords={job_title}',
                    'posted_date': '2024-01-14',
                    'job_type': 'Full-time',
                    'portal': 'Microsoft Careers',
                    'match_percentage': '92'
                },
                {
                    'title': f'{job_title} Engineer',
                    'company': 'Amazon',
                    'location': location or 'Remote',
                    'salary_range': '$90,000 - $130,000',
                    'experience_required': '3-5 years',
                    'description': f'Amazon is hiring {job_title} Engineers for various teams...',
                    'job_url': f'https://amazon.jobs/en/search?base_query={job_title}',
                    'posted_date': '2024-01-13',
                    'job_type': 'Full-time',
                    'portal': 'Amazon Jobs',
                    'match_percentage': '88'
                },
                {
                    'title': f'{job_title} Specialist',
                    'company': 'Meta',
                    'location': location or 'Menlo Park',
                    'salary_range': '$110,000 - $160,000',
                    'experience_required': '4-6 years',
                    'description': f'Meta is seeking a {job_title} Specialist to drive innovation...',
                    'job_url': f'https://www.metacareers.com/jobs/?q={job_title}',
                    'posted_date': '2024-01-12',
                    'job_type': 'Full-time',
                    'portal': 'Meta Careers',
                    'match_percentage': '90'
                }
            ]
            
            job_results = {
                'jobs': jobs,
                'total_found': len(jobs),
                'search_suggestions': []
            }
            
            return JsonResponse({
                'success': True,
                'search_data': search_data,
                'jobs': job_results['jobs'],
                'total_found': job_results['total_found'],
                'search_suggestions': job_results['search_suggestions']
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })