
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view # If you need function-based views later
from rest_framework import status # For HTTP status codes
from django.shortcuts import get_object_or_404 # Helper to get objects or return 404

# Import your models and serializers
from .models import Project, Country
from .serializers import ProjectSerializer, CountrySerializer, LeadOrgUnitSerializer, ThemeSerializer, DonorSerializer

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
