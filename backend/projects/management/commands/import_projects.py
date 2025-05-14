import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify # Useful for cleaning up names if needed
from decimal import Decimal, InvalidOperation # Import Decimal for monetary fields

# Import your models
from projects.models import Project, Country, LeadOrgUnit, Theme, Donor

class Command(BaseCommand):
    help = 'Imports project data from an Excel file.'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='The path to the Excel file to import.')
        parser.add_argument('--sheet', type=str, default=0, help='The sheet name or index (0-based) to import from.')

    def handle(self, *args, **options):
        file_path = options['excel_file']
        sheet_name = options['sheet']

        self.stdout.write(self.style.SUCCESS(f'Attempting to import data from "{file_path}"'))

        try:
            # Load the Excel file into a pandas DataFrame
            # pandas read_excel sheet_name can accept a string or an integer (0-based index)
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded sheet "{sheet_name}" from "{file_path}". Rows: {len(df)}'))

        except FileNotFoundError:
            raise CommandError(f'File not found at "{file_path}"')
        except Exception as e:
            raise CommandError(f'Error loading Excel file: {e}')

        # --- Data processing and import logic starts here ---

        # Keep track of imported/created counts
        created_count = 0
        updated_count = 0 # TODO:implement update later if needed
        skipped_count = 0
        theme_created_count = 0
        donor_created_count = 0

        # Iterate over DataFrame rows
        for index, row in df.iterrows():
            self.stdout.write(f'Processing row {index + 1}/{len(df)}...', ending='\r')


            # --- Extract data, handling potential NaN/NaT values ---
            # Use .get() for safety (returns None if column doesn't exist, though iterrows implies it does)
            # Check pd.isna() for pandas NA/NaN/NaT and map to Python's None

            # Handle Project ID (assuming it's numeric in Excel but stored as string)
            project_id_excel_raw = row.get('ProjectID')
            project_id_excel = None
            if pd.notna(project_id_excel_raw):
                 # Convert float/int to string. Assumes ProjectID is primarily numeric.
                 try:
                     project_id_excel = str(int(project_id_excel_raw)).strip() # to be safe
                 except (ValueError, TypeError):
                     # Handle cases where ProjectID might be non-numeric text unexpectedly
                     project_id_excel = str(project_id_excel_raw) # Just convert directly to string as a fallback
                     self.stdout.write(self.style.WARNING(f'Row {index + 1}: Non-numeric ProjectID "{project_id_excel_raw}". Storing as string.'))


            title = row.get('Project Title')
            if pd.isna(title) or not str(title).strip(): # Also check for empty string after conversion
                title = None

            paas_code = row.get('PAAS Code')
            if pd.isna(paas_code) or not str(paas_code).strip():
                 paas_code = None

            # --- Status Mapping ---
            # Map the string from Excel to the key in Project.STATUS_CHOICES
            excel_status = row.get('Approval Status')
            status = None # Default if mapping fails or data is missing
            if pd.notna(excel_status) and str(excel_status).strip():
                excel_status_cleaned = str(excel_status).strip()
                # Define your mapping - adjust the keys and values based on your Excel data
                status_mapping = {
                    'Approved': 'Approved',
                    'Pending Approval': 'Pending Approval',
                    # Add any other status strings you find in the Excel here
                    # 'Done': 'Approved', # Example mapping if 'Done' maps to 'Approved'
                    # 'Cancelled': 'Pending Approval', # Example of mapping to an existing key
                }
                status = status_mapping.get(excel_status_cleaned, None) # Get mapped status, or None if not found

                if status is None and excel_status_cleaned not in ['', 'nan', 'NaN', 'N/A']: # Don't warn for clearly empty cells
                     self.stdout.write(self.style.WARNING(f'Row {index + 1}: Unknown "Approval Status" value "{excel_status_cleaned}". Not mapping to a valid status.'))


            fund = row.get('Fund')
            if pd.isna(fund) or not str(fund).strip():
                 fund = None

            # Monetary fields - Use .get() and handle NaN/conversion errors
            # Note: Added Decimal import at the top
            monetary_fields = [
                ('PAG Value', 'pag_value'),
                ('Total Expenditure', 'total_expenditure'),
                ('Total Contribution', 'total_contribution'),
                ('Total Contribution - Total Expenditure', 'total_contribution_expenditure_diff'),
                ('Total PSC', 'total_psc'),
                # NOTE: 'Budget Amount' column is NOT in your Excel sample headers.
                # If it exists in your actual file, uncomment and add:
                # ('Budget Amount', 'budget_amount'),
            ]

            project_data = {} # Dictionary to hold extracted data for Project creation

            for excel_col, model_field in monetary_fields:
                value = row.get(excel_col)
                processed_value = None
                if pd.notna(value):
                    try:
                        # Clean up potential currency symbols, commas, etc. if necessary
                        # For now, assuming clean numbers or pandas has handled them
                        processed_value = Decimal(str(value)) # Convert via string for precision
                    except InvalidOperation:
                        self.stdout.write(self.style.WARNING(f'Row {index + 1}: Skipping invalid monetary value "{value}" for column "{excel_col}".'))
                        processed_value = None # Set to None if conversion fails
                    except Exception as e:
                         self.stdout.write(self.style.ERROR(f'Row {index + 1}: Unexpected error processing monetary value "{value}" for column "{excel_col}": {e}'))
                         processed_value = None

                project_data[model_field] = processed_value # Store in dictionary


            # Date fields - Handle pandas.NaT (Not a Time) and map to None
            # pandas datetime64[ns] objects are usually compatible with Django DateField
            start_date = row.get('Start Date')
            if pd.isnat(start_date):
                 start_date = None
            else:
                 # Convert pandas Timestamp to Python date if necessary, though often compatible
                 # If dates might be NaT or just blank cells, pd.to_datetime with errors='coerce'
                 # done *before* the loop could make this simpler, but this works too.
                 try:
                     if start_date: # Check if not None/NaT before accessing .date()
                         start_date = start_date.date()
                 except AttributeError:
                      # Handle cases where it's not a datetime object unexpectedly
                      self.stdout.write(self.style.WARNING(f'Row {index + 1}: Invalid Start Date format "{row.get("Start Date")}". Setting to None.'))
                      start_date = None


            end_date = row.get('End Date')
            if pd.isnat(end_date):
                 end_date = None
            else:
                 try:
                     if end_date:
                          end_date = end_date.date()
                 except AttributeError:
                      self.stdout.write(self.style.WARNING(f'Row {index + 1}: Invalid End Date format "{row.get("End Date")}". Setting to None.'))
                      end_date = None

            # Note: 'Approval Date' is in your model but not in the sample Excel headers.
            # If your actual file has this column, add extraction logic here:
            # approval_date = row.get('Approval Date')
            # if pd.isnat(approval_date): approval_date = None
            # else: try: if approval_date: approval_date = approval_date.date() except AttributeError: approval_date = None


            # --- Handle ForeignKey Relationships (Country, LeadOrgUnit) ---
            country_name = row.get('Country(ies)')
            country_obj = None
            if pd.notna(country_name) and str(country_name).strip():
                 country_name_cleaned = str(country_name).strip()
                 try:
                     country_obj, created = Country.objects.get_or_create(name=country_name_cleaned)
                     if created:
                         self.stdout.write(self.style.SUCCESS(f'Row {index + 1}: Created new Country: {country_name_cleaned}'))
                 except Exception as e:
                     self.stdout.write(self.style.ERROR(f'Row {index + 1}: Error getting/creating Country "{country_name_cleaned}": {e}'))


            lead_org_unit_name = row.get('Lead Org Unit')
            lead_org_unit_obj = None
            if pd.notna(lead_org_unit_name) and str(lead_org_unit_name).strip():
                 lead_org_unit_name_cleaned = str(lead_org_unit_name).strip()
                 try:
                     lead_org_unit_obj, created = LeadOrgUnit.objects.get_or_create(name=lead_org_unit_name_cleaned)
                     if created:
                         self.stdout.write(self.style.SUCCESS(f'Row {index + 1}: Created new Lead Org Unit: {lead_org_unit_name_cleaned}'))
                 except Exception as e:
                     self.stdout.write(self.style.ERROR(f'Row {index + 1}: Error getting/creating Lead Org Unit "{lead_org_unit_name_cleaned}": {e}'))


            # --- Check for mandatory fields before creating Project ---
            # Based on your model, title and status (if not null/blank) are mandatory.
            # Country and Lead Org Unit are null=True, blank=True, so they are technically optional.
            # Adjust this check if Country/Lead Org Unit are mandatory for a valid import entry.
            if title is None or status is None: # Check mandatory model fields
                 self.stdout.write(self.style.WARNING(f'Skipping row {index + 1} due to missing mandatory data (Title: {title}, Status: {status}).'))
                 skipped_count += 1
                 continue # Skip to the next row


            # --- Create the Project instance ---
            # Use get_or_create if you want to update existing projects based on a unique field like project_id_excel or paas_code
            # For now, we'll assume you want to create new ones or update if project_id_excel matches.
            # Let's implement a simple update-or-create based on project_id_excel

            try:
                # Attempt to get existing project by project_id_excel
                project, created = Project.objects.get_or_create(
                    project_id_excel=project_id_excel, # Use this as the lookup key
                    # Provide defaults for required fields if creating
                    defaults={
                        'title': title,
                        'status': status,
                        # Provide defaults for other fields (optional if null=True)
                        'paas_code': paas_code,
                        'fund': fund,
                        'start_date': start_date,
                        'end_date': end_date,
                        'country': country_obj,
                        'lead_org_unit': lead_org_unit_obj,
                        **project_data, # Unpack the monetary data
                        # 'approval_date': approval_date, # Uncomment if you added approval_date handling
                    }
                )

                if created:
                    created_count += 1
                else:
                    # If project exists, update its fields (excluding project_id_excel as it was used for lookup)
                    project.title = title
                    project.paas_code = paas_code
                    project.status = status
                    project.fund = fund
                    project.start_date = start_date
                    project.end_date = end_date
                    project.country = country_obj
                    project.lead_org_unit = lead_org_unit_obj
                    # Update monetary fields
                    for field, value in project_data.items():
                         setattr(project, field, value)
                    # if 'approval_date' in locals(): project.approval_date = approval_date # Uncomment if added
                    project.save() # Save the updates
                    updated_count += 1

                # --- Handle ManyToMany Relationships (Themes, Donors) AFTER saving the project ---
                # Clear existing relationships if you want the Excel data to be the source of truth
                # project.themes.clear()
                # project.donors.clear()

                # Themes
                themes_str = row.get('Theme(s)')
                if pd.notna(themes_str) and str(themes_str).strip():
                     # Split by comma, handle potential extra spaces around names
                     theme_names = [name.strip() for name in str(themes_str).split(',') if name.strip()]
                     for theme_name in theme_names:
                         try:
                             theme_obj, created = Theme.objects.get_or_create(name=theme_name)
                             if created:
                                 theme_created_count += 1
                                 # self.stdout.write(self.style.SUCCESS(f'Row {index + 1}: Created new Theme: {theme_name}')) # Optional: log theme creation
                             project.themes.add(theme_obj) # Add the theme to the project
                         except Exception as e:
                             self.stdout.write(self.style.ERROR(f'Row {index + 1}: Error getting/creating/adding Theme "{theme_name}": {e}'))

                # Donors
                donors_str = row.get('Donor(s)')
                if pd.notna(donors_str) and str(donors_str).strip():
                     # Split by comma, handle potential extra spaces around names
                     donor_names = [name.strip() for name in str(donors_str).split(',') if name.strip()]
                     for donor_name in donor_names:
                          try:
                             donor_obj, created = Donor.objects.get_or_create(name=donor_name)
                             if created:
                                donor_created_count += 1
                                # self.stdout.write(self.style.SUCCESS(f'Row {index + 1}: Created new Donor: {donor_name}')) # Optional: log donor creation
                             project.donors.add(donor_obj) # Add the donor to the project
                          except Exception as e:
                             self.stdout.write(self.style.ERROR(f'Row {index + 1}: Error getting/creating/adding Donor "{donor_name}": {e}'))


            except Exception as e:
                # Catch any errors during project get_or_create or save
                 self.stdout.write(self.style.ERROR(f'Row {index + 1}: Error processing project "{row.get("Project Title")}" (ID: {row.get("ProjectID")}): {e}'))
                 skipped_count += 1 # Count rows that failed to create/update Project


        # --- Data processing and import logic ends here ---

        # Clear the processing progress line before printing summary
        self.stdout.write('\r' + ' ' * 50 + '\r', ending='') # Clear the last progress message

        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Data Import Summary:'))
        self.stdout.write(self.style.SUCCESS(f'Processed Rows: {len(df)}'))
        self.stdout.write(self.style.SUCCESS(f'Projects Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Projects Updated: {updated_count}'))
        self.stdout.write(self.style.WARNING(f'Rows Skipped (due to errors or missing mandatory data): {skipped_count}'))
        self.stdout.write(self.style.SUCCESS(f'New Themes Created: {theme_created_count}'))
        self.stdout.write(self.style.SUCCESS(f'New Donors Created: {donor_created_count}'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Data import process finished.'))