# projects/views.py

import os
from dotenv import load_dotenv

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.pagination import PageNumberPagination

# Import your models and serializers
from .models import Project, Country, LeadOrgUnit, Theme, Donor
from .serializers import (
    ProjectSerializer,
    CountrySerializer,
    LeadOrgUnitSerializer,
    ThemeSerializer,
    DonorSerializer,
    CountryProjectCountSerializer,
    LeadOrgUnitProjectCountSerializer,
    ThemeProjectCountSerializer,
)

# --- Environment Variable Loading & AI Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    print("Warning: 'google-generativeai' library not found. AI insights will not be available.")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found. AI insights will not be available.")
elif genai:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring Gemini API: {e}. AI insights will not be available.")
        GEMINI_API_KEY = None
else:
    print("Warning: GEMINI_API_KEY is set, but 'google-generativeai' library is missing. AI insights cannot be initialized.")
    GEMINI_API_KEY = None

# --- Standard Pagination Configuration ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- Project ViewSet with Pagination and Filtering ---
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = [
        'title',
        'project_id_excel',
        'paas_code',
        'fund',
        'country__name',
        'donors__name',
        'themes__name',
        'lead_org_unit__name',
        'status'
    ]
    ordering_fields = ['title', 'created_at', 'status', 'country__name']
    ordering = ['-created_at']

    def get_queryset(self):
        return Project.objects.all().select_related(
            'country', 'lead_org_unit'
        ).prefetch_related(
            'themes', 'donors'
        ).order_by('-created_at')

# --- ViewSets for Related Models (New) ---

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Country data.
    Provides list and retrieve operations.
    Using ReadOnlyModelViewSet as CRUD might not be needed via API here.
    """
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    # No pagination needed for dropdown data usually, but you could add it if lists are very long.

class LeadOrgUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Lead Organization Unit data.
    Provides list and retrieve operations.
    """
    queryset = LeadOrgUnit.objects.all().order_by('name')
    serializer_class = LeadOrgUnitSerializer

class ThemeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Theme data.
    Provides list and retrieve operations.
    """
    queryset = Theme.objects.all().order_by('name')
    serializer_class = ThemeSerializer

class DonorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Donor data.
    Provides list and retrieve operations.
    """
    queryset = Donor.objects.all().order_by('name')
    serializer_class = DonorSerializer


# --- Custom Filtered List Views (Keep if still needed, otherwise can be removed) ---
# These are likely redundant if you use ProjectViewSet filtering but keeping for now.
class ProjectsByCountryView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        country_name = self.kwargs['country_name']
        country = get_object_or_404(Country, name__iexact=country_name)
        return Project.objects.filter(country=country).order_by('-created_at')

class ProjectsByStatusView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        status_key = self.kwargs['status_key']
        valid_status_keys = [key for key, value in Project.STATUS_CHOICES]
        if status_key not in valid_status_keys:
            raise ParseError(f"Invalid status key: '{status_key}'. Valid options are: {', '.join(valid_status_keys)}")
        return Project.objects.filter(status=status_key).order_by('-created_at')

# --- Dashboard Aggregation Views ---
class ProjectCountByCountryView(APIView):
    def get(self, request, *args, **kwargs):
        country_counts = Project.objects.filter(
            country__isnull=False
        ).values(
            'country__name'
        ).annotate(
            project_count=Count('id')
        ).order_by('-project_count', 'country__name')

        formatted_data = [
            {'country_name': item['country__name'], 'project_count': item['project_count']}
            for item in country_counts
        ]
        serializer = CountryProjectCountSerializer(formatted_data, many=True)
        return Response(serializer.data)

class ProjectCountByLeadOrgUnitView(APIView):
    def get(self, request, *args, **kwargs):
        org_unit_counts = Project.objects.filter(
            lead_org_unit__isnull=False
        ).values(
            'lead_org_unit__name'
        ).annotate(
            project_count=Count('id')
        ).order_by('-project_count', 'lead_org_unit__name')

        formatted_data = [
            {'org_unit_name': item['lead_org_unit__name'], 'project_count': item['project_count']}
            for item in org_unit_counts
        ]
        serializer = LeadOrgUnitProjectCountSerializer(formatted_data, many=True)
        return Response(serializer.data)

class ProjectCountByThemeView(APIView):
    def get(self, request, *args, **kwargs):
        theme_counts = Theme.objects.filter(
            projects__isnull=False
        ).annotate(
            project_count=Count('projects')
        ).values(
            'name', 'project_count'
        ).order_by('-project_count', 'name')

        serializer = ThemeProjectCountSerializer(theme_counts, many=True)
        return Response(serializer.data)

class WorldMapProjectDataView(APIView):
    def get(self, request, *args, **kwargs):
        country_counts = Project.objects.filter(
            country__isnull=False
        ).values(
            'country__name'
        ).annotate(
            project_count=Count('id')
        ).order_by('country__name')

        formatted_data = [
            {'country_name': item['country__name'], 'project_count': item['project_count']}
            for item in country_counts
        ]
        serializer = CountryProjectCountSerializer(formatted_data, many=True)
        return Response(serializer.data)

# --- AI Insights View ---
class AIInsightView(APIView):
    def get(self, request, *args, **kwargs):
        if not GEMINI_API_KEY or not genai:
            return Response(
                {"error": "AI service is not configured or unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            country_counts = Project.objects.filter(country__isnull=False).values('country__name').annotate(project_count=Count('id')).order_by('-project_count')[:10]
            theme_counts = Theme.objects.filter(projects__isnull=False).annotate(project_count=Count('projects')).values('name', 'project_count').order_by('-project_count')[:10]
            total_projects_count = Project.objects.count()

            country_list_str = "\n".join([f"- {item['country__name']}: {item['project_count']} projects" for item in country_counts]) if country_counts else "No data available for top countries."
            theme_list_str = "\n".join([f"- {item['name']}: {item['project_count']} projects" for item in theme_counts]) if theme_counts else "No data available for top themes."

            prompt_text = f"""
Analyze the following project data from UN-Habitat and provide a concise summary of key insights and trends.

Overall Project Count: {total_projects_count}

Top 10 Countries by Project Count:
{country_list_str}

Top 10 Themes by Project Count:
{theme_list_str}

Based on this data, highlight:
- The overall scale of the project portfolio.
- Key geographic areas of focus.
- Dominant thematic areas.
- Any notable patterns or observations.

Keep the summary concise and easy to understand, suitable for a dashboard display.
"""
            model_name = 'gemini-1.5-flash'
            try:
                pass # Optional model check removed for brevity
            except Exception as list_model_err:
                print(f"Could not list models to verify {model_name}: {list_model_err}")

            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt_text)

            if response and hasattr(response, 'text') and response.text:
                ai_insight = response.text
            elif response and response.candidates and response.candidates[0].content.parts[0].text:
                ai_insight = response.candidates[0].content.parts[0].text
            else:
                print("Gemini API returned an empty or improperly structured response.")
                return Response(
                    {"error": "AI service returned no insight. Content may be blocked or response structure unexpected."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({"insight": ai_insight}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"An error occurred in AIInsightView: {e}")
            return Response(
                {"error": f"An error occurred while processing AI insights: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
