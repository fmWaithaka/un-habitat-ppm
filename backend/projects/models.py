from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Consider adding a country code if available/useful e.g. K_CODE = models.CharField(max_length=3, unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Countries" # Correct pluralization in Django admin

    def __str__(self):
        return self.name

class LeadOrgUnit(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True) # Optional description

    class Meta:
        verbose_name_plural = "Lead Org Units"

    def __str__(self):
        return self.name

class Theme(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True) # Optional description

    def __str__(self):
        return self.name
    
class Donor(models.Model):
    name = models.CharField(max_length=200, unique=True)
    # Add other donor details if needed
    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved')
    ]

    title = models.CharField(max_length=255)

    project_id_excel = models.CharField(max_length=100, unique=True, null=True, blank=True)
    paas_code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Approved')
    fund = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='projects', null=True, blank=True) # Added null=True/blank=True as Country(ies) has missing data
    lead_org_unit = models.ForeignKey(LeadOrgUnit, on_delete=models.PROTECT, related_name='projects', null=True, blank=True) # Added null=True/blank=True as Lead Org Unit has missing data 
    themes = models.ManyToManyField(Theme, related_name='projects', blank=True) # ManyToMany
    approval_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Monetary/Numerical Fields -  DecimalField, map from float64
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    pag_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_expenditure = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_contribution = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_contribution_expenditure_diff = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # If you choose to store this
    total_psc = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Donor(s) - ManyToMany or TextField
    donors = models.ManyToManyField(Donor, related_name='projects', blank=True) # Structured relationship

    # Audit Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Default ordering for projects

    def __str__(self):
        return self.title