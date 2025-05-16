# projects/serializers.py

from rest_framework import serializers
from django.db import transaction
from .models import Project, Country, LeadOrgUnit, Theme, Donor

# Serializers for related models (used for read-only representation in ProjectSerializer output)
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name'] # Explicitly list fields, good practice

class LeadOrgUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadOrgUnit
        fields = ['id', 'name', 'description'] # Include description if useful

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'name', 'description'] # Include description if useful

class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = ['id', 'name']

# Main Project Serializer
class ProjectSerializer(serializers.ModelSerializer):
    # --- Read-only nested serializers for output ---
    # These provide detailed object representations when reading a project.
    # The `source` attribute points to the actual model field.
    country_detail = CountrySerializer(source='country', read_only=True)
    lead_org_unit_detail = LeadOrgUnitSerializer(source='lead_org_unit', read_only=True)
    themes_detail = ThemeSerializer(source='themes', many=True, read_only=True)
    donors_detail = DonorSerializer(source='donors', many=True, read_only=True)

    # --- Write-only string input fields for create/update ---
    # These fields will receive the string data from the frontend (e.g., "Kenya", "Urban Planning")
    # They are not actual model fields but are used during deserialization in create/update.
    country_name_input = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True,
        help_text="Name of the country. Will be used to find or create a Country object."
    )
    lead_org_unit_name_input = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True,
        help_text="Name of the Lead Org Unit. Will be used to find or create a LeadOrgUnit object."
    )
    themes_input = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True,
        help_text="Comma-separated string of theme names. Each name will be used to find or create a Theme object."
    )
    donors_input = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True,
        help_text="Comma-separated string of donor names. Each name will be used to find or create a Donor object."
    )

    # --- Read-only property from the model ---
    # This will automatically use the @property method from the Project model.
    total_contribution_expenditure_diff = serializers.DecimalField(
        max_digits=19, decimal_places=2, read_only=True, allow_null=True
    )

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

            # Write-only input fields (for create/update by name)
            'country_name_input',
            'lead_org_unit_name_input',
            'themes_input',
            'donors_input',

            # Read-only detail fields for output (using nested serializers)
            'country_detail',
            'lead_org_unit_detail',
            'themes_detail',
            'donors_detail',

            'created_at',
            'updated_at',
        ]

        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},

            'project_id_excel': {'required': False, 'allow_blank': True, 'allow_null': True},
            'paas_code': {'required': False, 'allow_blank': True, 'allow_null': True},
            'fund': {'required': False, 'allow_blank': True, 'allow_null': True},
            'approval_date': {'required': False, 'allow_null': True},
            'start_date': {'required': False, 'allow_null': True},
            'end_date': {'required': False, 'allow_null': True},
            'budget_amount': {'required': False, 'allow_null': True},
            'pag_value': {'required': False, 'allow_null': True},
            'total_expenditure': {'required': False, 'allow_null': True},
            'total_contribution': {'required': False, 'allow_null': True},
            'total_psc': {'required': False, 'allow_null': True},

            'title': {'required': True},
            'status': {'required': True},

            # Mark actual model relationship fields as write_only=True
            'country': {'write_only': True, 'required': False, 'allow_null': True},
            'lead_org_unit': {'write_only': True, 'required': False, 'allow_null': True},
            'themes': {'write_only': True, 'required': False},
            'donors': {'write_only': True, 'required': False},
        }


    def _handle_foreign_key(self, validated_data, input_field_name, model_field_name, related_model_class):
        """
        Helper to get or create a related object for a ForeignKey relationship.
        Pops the input_field_name from validated_data and sets the model_field_name.
        Handles cases where the input is None or an empty string.
        """
        name_input = validated_data.pop(input_field_name, None)

        # Only process if the input field was actually provided in the request
        if name_input is not None:
            if name_input.strip():
                obj, created = related_model_class.objects.get_or_create(
                    name__iexact=name_input.strip(),
                    defaults={'name': name_input.strip()}
                )
                validated_data[model_field_name] = obj
            else: # Handle empty string input by setting the ForeignKey to None
                 validated_data[model_field_name] = None
        # If name_input is None, it means the field wasn't in the request data (e.g., PATCH),
        # so we don't touch the existing instance's ForeignKey.


    def _handle_many_to_many(self, instance, validated_data, input_field_name, m2m_field_name, related_model_class):
        """
        Helper to get or create and set related objects for a ManyToMany relationship.
        Uses `validated_data.pop` to ensure it only runs if the input field was provided.
        Handles clearing the relation if an empty string is provided.
        """
        names_string = validated_data.pop(input_field_name, None)

        # Only proceed if the field was actually part of the input data
        if names_string is None:
            return # Do nothing if the field was not provided in the request

        m2m_manager = getattr(instance, m2m_field_name)

        if not names_string.strip(): # An empty string means clear the relation
            m2m_manager.clear()
            return

        name_list = [name.strip() for name in names_string.split(',') if name.strip()]
        obj_list = []
        for name in name_list:
            obj, _ = related_model_class.objects.get_or_create(
                name__iexact=name,
                defaults={'name': name}
            )
            obj_list.append(obj)
        m2m_manager.set(obj_list)


    @transaction.atomic
    def create(self, validated_data):
        # Handle ForeignKey relationships by name
        self._handle_foreign_key(validated_data, 'country_name_input', 'country', Country)
        self._handle_foreign_key(validated_data, 'lead_org_unit_name_input', 'lead_org_unit', LeadOrgUnit)

        # Pop M2M input strings; they will be handled after project instance creation.
        themes_input_string = validated_data.pop('themes_input', None)
        donors_input_string = validated_data.pop('donors_input', None)

        # Create the Project instance with remaining validated_data
        project = Project.objects.create(**validated_data)

        # Handle ManyToMany relationships by name, now that `project` instance exists.
        # We need to pass a dictionary to _handle_many_to_many because it expects to pop from it.
        if themes_input_string is not None:
             self._handle_many_to_many(project, {'themes_input': themes_input_string}, 'themes_input', 'themes', Theme)
        if donors_input_string is not None:
             self._handle_many_to_many(project, {'donors_input': donors_input_string}, 'donors_input', 'donors', Donor)

        return project

    @transaction.atomic
    def update(self, instance, validated_data):
        # Handle ForeignKey relationships by name.
        # The _handle_foreign_key helper uses validated_data.pop(..., None),
        # so it correctly handles cases where the input field is not present in the request data (PATCH).
        # We don't need the 'in self.initial_data' check here.
        self._handle_foreign_key(validated_data, 'country_name_input', 'country', Country)
        self._handle_foreign_key(validated_data, 'lead_org_unit_name_input', 'lead_org_unit', LeadOrgUnit)

        # Handle ManyToMany relationships by name.
        # The _handle_many_to_many helper also uses validated_data.pop(..., None),
        # so it correctly handles cases where the input field is not present.
        self._handle_many_to_many(instance, validated_data, 'themes_input', 'themes', Theme)
        self._handle_many_to_many(instance, validated_data, 'donors_input', 'donors', Donor)


        # Update standard fields on the instance with remaining validated_data.
        # This handles all fields that were not popped and handled above.
        # Only update fields that are actually present in validated_data.
        for attr, value in validated_data.items():
             # Check if the attribute exists on the model instance before setting
             # This prevents errors if unexpected fields somehow make it into validated_data
             if hasattr(instance, attr):
                setattr(instance, attr, value)
             else:
                 # Optional: Log a warning if an unexpected field is found
                 print(f"Warning: Attempted to set unknown attribute '{attr}' on Project instance.")


        instance.save() # Save the instance with updated standard fields

        return instance


# --- Serializers for Dashboard Aggregated Data ---
# (These should be fine as they are for read-only aggregation)

class CountryProjectCountSerializer(serializers.Serializer):
    country_name = serializers.CharField(max_length=150) # Match model's max_length
    project_count = serializers.IntegerField()

class LeadOrgUnitProjectCountSerializer(serializers.Serializer):
    org_unit_name = serializers.CharField(max_length=255) # Match model's max_length
    project_count = serializers.IntegerField()

class ThemeProjectCountSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255) # Match model's max_length
    project_count = serializers.IntegerField()

# World Map Serializer (can reuse CountryProjectCountSerializer if structure matches)
# class WorldMapProjectDataSerializer(serializers.Serializer):
#     country_name = serializers.CharField()
#     value = serializers.IntegerField() # e.g., project_count or total_budget
