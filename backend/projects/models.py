from django.db import models
from django.core.exceptions import ValidationError

class Country(models.Model):
    name = models.CharField(max_length=150, unique=True) # Increased max_length for potentially longer country names
    # Consider adding a country code if available/useful e.g. K_CODE = models.CharField(max_length=3, unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Countries" # Correct pluralization in Django admin

    def __str__(self):
        return self.name

class LeadOrgUnit(models.Model):
    name = models.CharField(max_length=255, unique=True) # Increased max_length
    description = models.TextField(blank=True, null=True) # Optional description

    class Meta:
        verbose_name_plural = "Lead Org Units"

    def __str__(self):
        return self.name

class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True) # Increased max_length for longer theme names like "Urban Land, Legislation & Governance"
    description = models.TextField(blank=True, null=True) # Optional description

    def __str__(self):
        return self.name
    
class Donor(models.Model):
    name = models.CharField(max_length=255, unique=True) # Increased max_length for longer donor names
    # Add other donor details if needed
    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        # Add other statuses if they exist in your full dataset
        ('Implemented', 'Implemented'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=500) # Increased max_length for very long project titles

    # project_id_excel: Using CharField for flexibility, as ProjectID might contain non-numeric or have specific formatting.
    # The sample '1000.0' could be stored as "1000.0" or "1000". If it's always a number and used for sorting/math, consider FloatField.
    project_id_excel = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="Project ID as it appears in the Excel/source data.")
    paas_code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending Approval') # Changed default, review if 'Approved' is better
    fund = models.CharField(max_length=100, null=True, blank=True)
    
    # Relationships
    country = models.ForeignKey(
        Country, 
        on_delete=models.SET_NULL, # Changed from PROTECT to SET_NULL to allow deleting a country without deleting projects, set project.country to NULL instead. Review this choice.
        related_name='projects', 
        null=True, 
        blank=True,
        help_text="Primary country of project implementation. Can be null if global or not specified."
    )
    lead_org_unit = models.ForeignKey(
        LeadOrgUnit, 
        on_delete=models.SET_NULL, # Changed from PROTECT to SET_NULL. Review this choice.
        related_name='projects', 
        null=True, 
        blank=True
    )
    themes = models.ManyToManyField(Theme, related_name='projects', blank=True)
    donors = models.ManyToManyField(Donor, related_name='projects', blank=True) # Structured relationship

    # Dates
    approval_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Monetary/Numerical Fields - DecimalField for precision
    # max_digits and decimal_places can be adjusted based on the maximum possible values.
    # The sample values like 4,218,607.0 fit well.
    budget_amount = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    pag_value = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True) # From sample
    total_expenditure = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True) # From sample
    total_contribution = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True) # From sample
    total_psc = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True) # From sample

    # Audit Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', 'title'] # Default ordering

    def __str__(self):
        return f"{self.title} ({self.project_id_excel or 'N/A'})"

    @property
    def total_contribution_expenditure_diff(self):
        """
        Calculates the difference between total contribution and total expenditure.
        Returns None if either value is not set.
        """
        if self.total_contribution is not None and self.total_expenditure is not None:
            return self.total_contribution - self.total_expenditure
        return None

    def clean(self):
        """
        Custom validation for the model.
        """
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be before the start date.'})
        # Add other model-level validations here

    # def save(self, *args, **kwargs):
    #     # If you were storing total_contribution_expenditure_diff, you'd calculate it here:
    #     # if self.total_contribution is not None and self.total_expenditure is not None:
    #     #    self.total_contribution_expenditure_diff = self.total_contribution - self.total_expenditure
    #     # else:
    #     #    self.total_contribution_expenditure_diff = None
    #     super().save(*args, **kwargs)
