# https://github.com/sk1ldpadde/OMNISTUDYIN
from rest_framework import serializers
from .models import Project, Country, LeadOrgUnit, Theme, Donor

# Serializer for the Country model
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__' # Include all fields from the Country model

# Serializer for the LeadOrgUnit model
class LeadOrgUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadOrgUnit
        fields = '__all__' # Include all fields

# Serializer for the Theme model
class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__' # Include all fields

# Serializer for the Donor model
class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__' # Include all fields

# Main Project Serializer
class ProjectSerializer(serializers.ModelSerializer):
    # Use the nested serializers for read-only representation
    country = CountrySerializer(read_only=True)
    lead_org_unit = LeadOrgUnitSerializer(read_only=True)
    themes = ThemeSerializer(many=True, read_only=True)
    donors = DonorSerializer(many=True, read_only=True)

    # Note: For create/update operations, you might need to handle
    # the incoming data for country, lead_org_unit, themes, and donors
    # differently (e.g., using PrimaryKeyRelatedField, SlugRelatedField
    # with write=True, or custom create/update methods in this serializer)
    # depending on how your frontend sends the data (IDs vs. names).
    # The current setup assumes frontend sends IDs for ForeignKey/ManyToMany
    # or you have custom logic elsewhere.
    # If using text inputs on the frontend for related objects by name,
    # you MUST add custom logic in the create/update methods here.

    class Meta:
        model = Project
        fields = [
            'id',
            'project_id_excel',
            'title',
            'paas_code',
            'status',
            'fund',
            'approval_date',
            'start_date',
            'end_date',
            'budget_amount',
            'pag_value',
            'total_expenditure',
            'total_contribution',
            'total_contribution_expenditure_diff',
            'total_psc',
            'created_at',
            'updated_at',
            'country', # This field will use the nested CountrySerializer for output
            'lead_org_unit', # Uses nested LeadOrgUnitSerializer
            'themes', # Uses nested ThemeSerializer (many=True)
            'donors', # Uses nested DonorSerializer (many=True)
        ]
        # Add extra_kwargs for fields that might be read-only or have specific requirements
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            # If project_id_excel should not be updated after creation:
            # 'project_id_excel': {'read_only': True},
        }


# --- Serializers for Dashboard Aggregated Data ---

class CountryProjectCountSerializer(serializers.Serializer):
    """Serializer for project count aggregated by Country."""
    # These field names must match the keys returned by the Django ORM .values().annotate() query
    country_name = serializers.CharField(max_length=100)
    project_count = serializers.IntegerField()

class LeadOrgUnitProjectCountSerializer(serializers.Serializer):
    """Serializer for project count aggregated by Lead Organization Unit."""
    # These field names must match the keys returned by the Django ORM .values().annotate() query
    org_unit_name = serializers.CharField(max_length=200)
    project_count = serializers.IntegerField()

class ThemeProjectCountSerializer(serializers.Serializer):
    """Serializer for project count aggregated by Theme."""
     # These field names must match the keys returned by the Django ORM .values().annotate() query
    # CHANGED 'theme_name' to 'name' to match the ORM query output
    name = serializers.CharField(max_length=150) # Matches 'name' from Theme model values()
    project_count = serializers.IntegerField() # Matches the annotated count field

# Serializer for World Map data (reusing Country count for simplicity as planned)
# If the map library needs a different structure (e.g., country code, or a 'value' field),
# you would modify this serializer and the corresponding view query.
# For now, it's the same structure as CountryProjectCountSerializer.
# class WorldMapProjectDataSerializer(serializers.Serializer):
#     country_name = serializers.CharField(max_length=100)
#     value = serializers.IntegerField() # e.g., project_count or total_budget

