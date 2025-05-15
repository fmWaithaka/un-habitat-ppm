# projects/views.py

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view # If you need function-based views later
from rest_framework import status # For HTTP status codes
from django.shortcuts import get_object_or_404 # Helper to get objects or return 404

# Import Count for aggregation
from django.db.models import Count

# Import APIView for custom views
from rest_framework.views import APIView


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

# Optional: Import django-filter for more complex filtering if needed later
# from rest_framework import filters

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
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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
            # Return an empty queryset or raise an error if the status key is invalid
            # Raising an error gives clearer feedback to the API user
            from rest_framework.exceptions import ParseError
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


# --- New Views for Dashboard Aggregated Data ---

class ProjectCountByCountryView(APIView):
    """API view to get project count aggregated by Country."""
    def get(self, request, *args, **kwargs):
        # Aggregate projects by country and count them
        # Use values('country__name') to group by the country's name
        # Use annotate(project_count=Count('id')) to count projects in each group
        # Use filter(country__isnull=False) to exclude projects without a country
        # Use order_by('country__name') to order the results
        country_counts = Project.objects.filter(
            country__isnull=False # Only include projects with a country assigned
        ).values(
            'country__name' # Group by country name
        ).annotate(
            project_count=Count('id') # Count projects in each group
        ).order_by('country__name') # Order results by country name

        # Rename the 'country__name' key to 'country_name' to match the serializer
        # This step is necessary because values() returns keys like 'country__name'
        # We can do this manually or use a serializer method field if needed,
        # but a list comprehension is straightforward here.
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
        # Similar logic to country aggregation
        org_unit_counts = Project.objects.filter(
            lead_org_unit__isnull=False # Only include projects with an org unit assigned
        ).values(
            'lead_org_unit__name' # Group by org unit name
        ).annotate(
            project_count=Count('id') # Count projects
        ).order_by('lead_org_unit__name') # Order results

        # Format the data to match the serializer
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
        # For ManyToMany fields, aggregation works slightly differently.
        # We can aggregate on the Theme model and count related projects.
        theme_counts = Theme.objects.filter(
             projects__isnull=False # Only include themes that have at least one project
        ).annotate(
            project_count=Count('projects') # Count projects related to each theme
        ).values(
            'name', # Group by theme name
            'project_count' # Include the calculated count
        ).order_by('name') # Order results by theme name

        # The values() call here directly returns keys 'name' and 'project_count',
        # which match the serializer fields, so no manual renaming is needed.
        formatted_data = list(theme_counts) # Convert queryset to list

        # Serialize the aggregated data
        serializer = ThemeProjectCountSerializer(formatted_data, many=True)

        return Response(serializer.data)

# View for World Map data (reusing Country count for simplicity)
# If the map requires a different structure or data (e.g., budget),
# you would modify the query and potentially use a different serializer.
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

        # Format the data to match the expected structure for a map library
        # (e.g., often requires country name/code and a value)
        # We'll use country_name and project_count, which fits CountryProjectCountSerializer
        formatted_data = [
            {'country_name': item['country__name'], 'project_count': item['project_count']}
            for item in country_counts
        ]

        # Serialize the data (reusing CountryProjectCountSerializer)
        serializer = CountryProjectCountSerializer(formatted_data, many=True)

        return Response(serializer.data)
