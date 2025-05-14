from django.contrib import admin
from .models import Country, LeadOrgUnit, Theme, Donor, Project

# Basic registration
admin.site.register(Country)
admin.site.register(LeadOrgUnit)
admin.site.register(Theme)
admin.site.register(Donor)
# admin.site.register(Project) 

# Customized Admin for Project (optional but recommended)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'lead_org_unit', 'status', 'fund', 'start_date', 'end_date', 'budget_amount', 'updated_at')
    list_filter = ('status', 'country', 'lead_org_unit', 'themes', 'donors')
    search_fields = ('title', 'description', 'project_id_excel', 'paas_code')
    # For ManyToMany fields, you might want a more user-friendly widget
    filter_horizontal = ('themes', 'donors') 
    # You can also define fieldsets for a more organized edit page
    # fieldsets = (
    #     (None, {
    #         'fields': ('title', 'project_id_excel', 'paas_code', 'description')
    #     }),
    #     ('Location & Organization', {
    #         'fields': ('country', 'lead_org_unit')
    #     }),
    #     ('Status & Dates', {
    #         'fields': ('status', 'approval_date', 'start_date', 'end_date')
    #     }),
    #     ('Financials', {
    #         'fields': ('budget_amount', 'pag_value', 'total_expenditure', 'total_contribution', 'total_contribution_expenditure_diff', 'total_psc')
    #     }),
    #     ('Categorization', {
    #         'fields': ('themes', 'donors')
    #     }),
    # )
    # readonly_fields = ('created_at', 'updated_at') # Make these read-only in admin

admin.site.register(Project, ProjectAdmin) # Register Project with the custom admin options