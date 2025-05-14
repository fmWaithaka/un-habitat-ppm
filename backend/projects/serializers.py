# https://github.com/sk1ldpadde/OMNISTUDYIN
from rest_framework import serializers
from .models import Project, Country, LeadOrgUnit, Theme, Donor

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__' # Include all fields from the Country model

class LeadOrgUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadOrgUnit
        fields = '__all__' # Include all fields

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__' # Include all fields

class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__' # Include all fields

class ProjectSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    lead_org_unit = LeadOrgUnitSerializer(read_only=True)
    themes = ThemeSerializer(many=True, read_only=True)
    donors = DonorSerializer(many=True, read_only=True)

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
            'country',
            'lead_org_unit',
            'themes',
            'donors',
        ]
    