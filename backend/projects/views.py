# projects/views.py

import os
import re # Import the regular expression module
from dotenv import load_dotenv

from django.db.models import Count, Q, Sum # Import Sum for aggregations
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
    # You might need new serializers for value aggregations and KPIs
    # For now, we'll use simple dictionaries or existing serializers if applicable
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

# --- ViewSets for Related Models ---

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Country data.
    Provides list and retrieve operations.
    """
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer

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


# --- Custom Filtered List Views (Keep if still needed) ---
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

# --- Dashboard Aggregation Views (Existing and New) ---

class ProjectCountByCountryView(APIView):
    """Aggregates project counts by country."""
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
        # Using existing serializer, might need a dedicated one if structure changes
        serializer = CountryProjectCountSerializer(formatted_data, many=True)
        return Response(serializer.data)

class ProjectCountByLeadOrgUnitView(APIView):
    """Aggregates project counts by lead organization unit."""
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
        # Using existing serializer
        serializer = LeadOrgUnitProjectCountSerializer(formatted_data, many=True)
        return Response(serializer.data)

class ProjectCountByThemeView(APIView):
    """Aggregates project counts by theme."""
    def get(self, request, *args, **kwargs):
        theme_counts = Theme.objects.filter(
            projects__isnull=False
        ).annotate(
            project_count=Count('projects')
        ).values(
            'name', 'project_count'
        ).order_by('-project_count', 'name')

        # Using existing serializer
        serializer = ThemeProjectCountSerializer(theme_counts, many=True)
        return Response(serializer.data)

class WorldMapProjectDataView(APIView):
     """Provides data for the world map (project count by country)."""
     # This view is similar to ProjectCountByCountryView, keeping for clarity
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
         # Using existing serializer
         serializer = CountryProjectCountSerializer(formatted_data, many=True)
         return Response(serializer.data)

# --- NEW Dashboard KPI View ---
class DashboardKPIsView(APIView):
    """Provides key performance indicators for the dashboard."""
    def get(self, request, *args, **kwargs):
        # Calculate total counts and sums
        total_projects_count = Project.objects.count()
        total_pag_value = Project.objects.aggregate(Sum('pag_value'))['pag_value__sum'] or 0
        total_expenditure = Project.objects.aggregate(Sum('total_expenditure'))['total_expenditure__sum'] or 0
        total_contribution = Project.objects.aggregate(Sum('total_contribution'))['total_contribution__sum'] or 0 # Assuming total_contribution exists
        # Calculate financial health (Total Contribution - Total Expenditure)
        overall_financial_health = total_contribution - total_expenditure

        # Calculate unique counts for related models with active projects
        unique_countries_count = Project.objects.filter(country__isnull=False).values('country').distinct().count()
        unique_lead_org_units_count = Project.objects.filter(lead_org_unit__isnull=False).values('lead_org_unit').distinct().count()
        unique_themes_count = Project.objects.filter(themes__isnull=False).values('themes').distinct().count()


        kpis_data = {
            'total_projects_count': total_projects_count,
            'total_pag_value': float(total_pag_value), # Ensure float for JSON serialization
            'total_expenditure': float(total_expenditure), # Ensure float
            'total_contribution': float(total_contribution), # Ensure float
            'overall_financial_health': float(overall_financial_health), # Ensure float
            'unique_countries_count': unique_countries_count,
            'unique_lead_org_units_count': unique_lead_org_units_count,
            'unique_themes_count': unique_themes_count,
        }

        # No specific serializer needed for this simple dictionary response
        return Response(kpis_data, status=status.HTTP_200_OK)

# --- NEW Dashboard Value Aggregation Views ---
class ValueByCountryView(APIView):
    """Aggregates total PAG value by country and splits into single vs combined/regional."""
    def get(self, request, *args, **kwargs):
        country_values = Project.objects.filter(
            country__isnull=False,
            pag_value__isnull=False
        ).values(
            'country__name'
        ).annotate(
            total_pag_value=Sum('pag_value')
        ).order_by('-total_pag_value', 'country__name')

        single_countries_data = []
        combined_data = []

        # Define patterns to identify combined/regional/global entries (case-insensitive)
        # Added a pattern for "United Nations Organization" as it's also a non-geographic entity
        combined_patterns = [
            r'GLOBAL',
            r'Regional',
            r',', # Assuming entries with commas are multi-country
            r'United Nations Organization' # Added pattern for this specific entry
        ]

        for item in country_values:
            country_name = item['country__name']
            total_pag_value = float(item['total_pag_value'] or 0) # Ensure 0 if sum is None

            # Check if the country name matches any combined pattern using re.search
            is_combined = any(re.search(pattern, country_name, re.IGNORECASE) for pattern in combined_patterns)

            if is_combined:
                # Use 'name' and 'value' keys for consistency with charting components
                combined_data.append({'name': country_name, 'value': total_pag_value})
            else:
                # Use 'name' and 'value' keys for consistency with charting components
                single_countries_data.append({'name': country_name, 'value': total_pag_value})

        # Return an object containing both lists
        return Response({
            'single_countries_data': single_countries_data,
            'combined_data': combined_data
        }, status=status.HTTP_200_OK)


class ValueByLeadOrgView(APIView):
    """Aggregates total PAG value by lead organization unit."""
    def get(self, request, *args, **kwargs):
        org_unit_values = Project.objects.filter(
            lead_org_unit__isnull=False,
            pag_value__isnull=False
        ).values(
            'lead_org_unit__name'
        ).annotate(
            total_pag_value=Sum('pag_value')
        ).order_by('-total_pag_value', 'lead_org_unit__name')

        formatted_data = [
            {'name': item['lead_org_unit__name'], 'value': float(item['total_pag_value'] or 0)} # Use 'name' and 'value' for consistency, ensure 0 if sum is None
            for item in org_unit_values
        ]
        return Response(formatted_data, status=status.HTTP_200_OK)

class ValueByThemeView(APIView):
    """Aggregates total PAG value by theme."""
    def get(self, request, *args, **kwargs):
        theme_values = Theme.objects.filter(
             projects__pag_value__isnull=False # Filter themes linked to projects with PAG value
        ).annotate(
             total_pag_value=Sum('projects__pag_value')
        ).values(
             'name', 'total_pag_value'
        ).order_by('-total_pag_value', 'name')

        # Format data for response
        formatted_data = [
             {'name': item['name'], 'value': float(item['total_pag_value'] or 0)} # Use 'name' and 'value' for consistency, ensure 0 if sum is None
             for item in theme_values
        ]
        return Response(formatted_data, status=status.HTTP_200_OK)


# --- AI Insights View ---
class AIInsightView(APIView):
    """Provides AI-generated insights based on project data."""
    def get(self, request, *args, **kwargs):
        if not GEMINI_API_KEY or not genai:
            return Response(
                {"error": "AI service is not configured or unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Fetch data for AI prompt
            country_counts = Project.objects.filter(country__isnull=False).values('country__name').annotate(project_count=Count('id')).order_by('-project_count')[:10]
            theme_counts = Theme.objects.filter(projects__isnull=False).annotate(project_count=Count('projects')).values('name', 'project_count').order_by('-project_count')[:10]
            total_projects_count = Project.objects.count()
            total_pag_value = Project.objects.aggregate(Sum('pag_value'))['pag_value__sum'] or 0


            country_list_str = "\n".join([f"- {item['country__name']}: {item['project_count']} projects" for item in country_counts]) if country_counts else "No data available for top countries."
            theme_list_str = "\n".join([f"- {item['name']}: {item['project_count']} projects" for item in theme_counts]) if theme_counts else "No data available for top themes."

            prompt_text = f"""
Analyze the following project data from UN-Habitat and provide a concise summary of key insights and trends.

Overall Project Count: {total_projects_count}
Total PAG Value: {total_pag_value}

Top 10 Countries by Project Count:
{country_list_str}

Top 10 Themes by Project Count:
{theme_list_str}

Based on this data, highlight:
- The overall scale of the project portfolio and total value.
- Key geographic areas of focus.
- Dominant thematic areas.
- Any notable patterns or observations.

Keep the summary concise and easy to understand, suitable for a dashboard display.
"""
            model_name = 'gemini-1.5-flash'
            try:
                # Optional: Verify model availability (can be slow, often removed in production)
                # list(genai.list_models()) # This line is commented out for performance
                pass
            except Exception as list_model_err:
                print(f"Could not list models to verify {model_name}: {list_model_err}")


            model = genai.GenerativeModel(model_name)
            # Use generate_content directly
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
