# projects/views.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view # Keep if you need function-based views later
from rest_framework.exceptions import ParseError # Import ParseError as used in ProjectsByStatusView

# Optional: Import django-filter for more complex filtering if needed later
# from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend # Keep if using DjangoFilterBackend


# Import your models and serializers
from .models import Project, Country, LeadOrgUnit, Theme, Donor
from .serializers import (
    ProjectSerializer,
    CountrySerializer,
    LeadOrgUnitSerializer,
    ThemeSerializer,
    DonorSerializer,
    # Import the new dashboard serializers
    CountryProjectCountSerializer,
    LeadOrgUnitProjectCountSerializer,
    ThemeProjectCountSerializer,
    # WorldMapProjectDataSerializer # If you created a separate one
)


# Load environment variables from .env file as early as possible
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the generative AI library if the API key is available
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables. AI insights will not be available.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Optional: Verify configuration by listing models (can be noisy in logs)
        # print("Gemini API configured successfully.")
        # list(genai.list_models()) # Attempt to list to check connection/auth
    except Exception as e:
        # Catch potential errors during configuration itself
        print(f"Error configuring Gemini API: {e}. AI insights will not be available.")
        # Set key to None or handle error state if configuration fails after finding key
        GEMINI_API_KEY = None # Ensure it's treated as missing if config fails


# --- ViewSet for standard Project CRUD ---
# ModelViewSet provides list, create, retrieve, update, partial_update, and destroy actions
class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    Handles GET (list, retrieve), POST, PUT, PATCH, DELETE for projects.
    """
    queryset = Project.objects.all().order_by('-created_at') # Default queryset for listing
    serializer_class = ProjectSerializer
    # Optional: Add filtering, searching, ordering capabilities
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['status', 'country__name', 'lead_org_unit__name', 'themes__name', 'donors__name'] # Example filters
    # search_fields = ['title', 'description', 'project_id_excel', 'paas_code', 'fund'] # Example search


# --- Custom Generic Views for specific filtering ---

class ProjectsByCountryView(generics.ListAPIView):
    """
    API endpoint that lists projects filtered by country name.
    GET /api/projects/country/{country_name}/
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        This view should return a list of all projects for
        the country name as determined by the URL portion.
        """
        country_name = self.kwargs['country_name'] # Get the country name from the URL
        # Find the Country object based on the name, or return 404 if not found
        country = get_object_or_404(Country, name__iexact=country_name) # __iexact for case-insensitive match
        # Return projects related to this country object
        return Project.objects.filter(country=country).order_by('-created_at')

class ProjectsByStatusView(generics.ListAPIView):
    """
    API endpoint that lists projects filtered by status key.
    GET /api/projects/status/{status_key}/
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        This view should return a list of all projects for
        the status key as determined by the URL portion.
        """
        status_key = self.kwargs['status_key'] # Get the status key from the URL
        # Check if the provided status_key is one of the valid choices
        valid_status_keys = [key for key, value in Project.STATUS_CHOICES]
        if status_key not in valid_status_keys:
            # Raising an error gives clearer feedback to the API user
            raise ParseError(f"Invalid status key: '{status_key}'. Valid options are: {', '.join(valid_status_keys)}")

        # Return projects with the matching status key
        return Project.objects.filter(status=status_key).order_by('-created_at')

# --- Optional: Views for other models if you need separate endpoints ---
# You might not need these if you only access them via the Project serializer,
# but they are useful if you need to list all countries, themes, etc.

# class CountryListView(generics.ListAPIView):
#     queryset = Country.objects.all().order_by('name')
#     serializer_class = CountrySerializer

# class ThemeListView(generics.ListAPIView):
#     queryset = Theme.objects.all().order_by('name')
#     serializer_class = ThemeSerializer

# ... etc for LeadOrgUnit and Donor


# --- API Views for Dashboard Aggregated Data ---

class ProjectCountByCountryView(APIView):
    """API view to get project count aggregated by Country."""
    def get(self, request, *args, **kwargs):
        # Aggregate projects by country and count them
        country_counts = Project.objects.filter(
            country__isnull=False
        ).values(
            'country__name'
        ).annotate(
            project_count=Count('id')
        ).order_by('country__name')

        # Explicitly format the data to match the serializer field names
        formatted_data = [
            {'country_name': item['country__name'], 'project_count': item['project_count']}
            for item in country_counts
        ]

        # Serialize the aggregated data
        serializer = CountryProjectCountSerializer(formatted_data, many=True)
        return Response(serializer.data)


class ProjectCountByLeadOrgUnitView(APIView):
    """API view to get project count aggregated by Lead Organization Unit."""
    def get(self, request, *args, **kwargs):
        # Aggregate projects by lead_org_unit and count them
        org_unit_counts = Project.objects.filter(
            lead_org_unit__isnull=False
        ).values(
            'lead_org_unit__name'
        ).annotate(
            project_count=Count('id')
        ).order_by('lead_org_unit__name')

        # Explicitly format the data to match the serializer field names
        formatted_data = [
            {'org_unit_name': item['lead_org_unit__name'], 'project_count': item['project_count']}
            for item in org_unit_counts
        ]

        # Serialize the aggregated data
        serializer = LeadOrgUnitProjectCountSerializer(formatted_data, many=True)
        return Response(serializer.data)


class ProjectCountByThemeView(APIView):
    """API view to get project count aggregated by Theme."""
    def get(self, request, *args, **kwargs):
        # Aggregate projects by themes and count them
        theme_counts = Theme.objects.filter(
             projects__isnull=False
        ).annotate(
            project_count=Count('projects')
        ).values(
            'name',
            'project_count'
        ).order_by('name')

        # values() returns a QuerySet which is iterable, pass directly
        # Note: The keys 'name' and 'project_count' from values() already match the serializer fields
        serializer = ThemeProjectCountSerializer(theme_counts, many=True)
        return Response(serializer.data)


class WorldMapProjectDataView(APIView):
    """API view to get data for World Map visualization (project count by country)."""
    def get(self, request, *args, **kwargs):
        # Reuse the aggregation logic from ProjectCountByCountryView
        country_counts = Project.objects.filter(
            country__isnull=False
        ).values(
            'country__name'
        ).annotate(
            project_count=Count('id')
        ).order_by('country__name')

        # Explicitly format the data to match the expected structure for a map library
        # (e.g., often requires country name/code and a value)
        # We'll use country_name and project_count, which fits CountryProjectCountSerializer
        formatted_data = [
            {'country_name': item['country__name'], 'project_count': item['project_count']}
            for item in country_counts
        ]

        # Serialize the data (reusing CountryProjectCountSerializer)
        serializer = CountryProjectCountSerializer(formatted_data, many=True)

        return Response(serializer.data)


# --- API View for AI Insights ---
class AIInsightView(APIView):
    """API view to generate AI insights using Gemini."""

    def get(self, request, *args, **kwargs):
        # Check if the Gemini API key is available before proceeding
        if not GEMINI_API_KEY:
            return Response(
                {"error": "AI service is not configured. GEMINI_API_KEY environment variable not set or configuration failed."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE # Use 503 if a required external service is unavailable
            )

        try:
            # --- 1. Fetch Data for Analysis ---
            # Fetch aggregated data to provide context to the AI.

            # Fetch top 10 countries by project count
            country_counts = Project.objects.filter(
                country__isnull=False
            ).values('country__name').annotate(project_count=Count('id')).order_by('-project_count')[:10]

            # Fetch top 10 themes by project count
            theme_counts = Theme.objects.filter(
                 projects__isnull=False
            ).annotate(project_count=Count('projects')).values('name', 'project_count').order_by('-project_count')[:10]

            # Get the total number of projects
            total_projects_count = Project.objects.count()

            # --- 2. Construct the Prompt for Gemini ---
            # Build the multi-line strings for the lists
            country_list_str = "No data available for top countries."
            if country_counts:
                country_list_lines = [f"- {item['country__name']}: {item['project_count']} projects" for item in country_counts]
                country_list_str = "\n".join(country_list_lines)

            theme_list_str = "No data available for top themes."
            if theme_counts:
                 theme_list_lines = [f"- {item['name']}: {item['project_count']} projects" for item in theme_counts]
                 theme_list_str = "\n".join(theme_list_lines)


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

            # --- 3. Call the Gemini API ---
            model = genai.GenerativeModel('gemini-2.0-flash')

            try:
                response = model.generate_content(prompt_text)
                # Access the generated text. Handle cases where content might be blocked or empty.
                if response and response.text:
                    ai_insight = response.text
                    # print("Gemini generated insight successfully.") # Optional log
                else:
                     # Handle cases where response is empty or blocked
                     print("Gemini API returned an empty or blocked response.")
                     return Response(
                         {"error": "AI service returned no insight. Content may be blocked."},
                         status=status.HTTP_500_INTERNAL_SERVER_ERROR # Or 400 if prompt is the issue
                     )


            except Exception as gemini_error:
                print(f"Error calling Gemini API: {gemini_error}")
                return Response(
                    {"error": f"Failed to generate AI insights from Gemini: {gemini_error}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # --- 4. Return the Generated Insight ---
            return Response({"insight": ai_insight}, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch any other unexpected errors during data fetching or processing
            print(f"An unexpected error occurred in AIInsightView: {e}")
            return Response(
                {"error": f"An unexpected error occurred while processing AI insights: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
