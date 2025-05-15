# backend/projects/management/commands/import_projects.py

import csv
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify # Useful if you need slugs, not strictly needed here
from django.utils import timezone # For handling dates/datetimes
from decimal import Decimal, InvalidOperation # For DecimalField

# Import your models
from projects.models import Project, Country, LeadOrgUnit, Theme, Donor

class Command(BaseCommand):
    help = 'Imports projects from a CSV file.'

    def add_arguments(self, parser):
        # Add a command line argument to specify the path to the CSV file
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import')

        # Optional: Add an argument to clear existing data before importing
        parser.add_argument(
            '--clear',
            action='store_true', # This makes it a flag (no value needed)
            help='Clear existing project data before importing',
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        clear_data = options['clear']

        # --- Optional: Clear existing data ---
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing project data...'))
            Project.objects.all().delete()
            # Optionally clear related models if you are re-importing everything
            # Country.objects.all().delete()
            # LeadOrgUnit.objects.all().delete()
            # Theme.objects.all().delete()
            # Donor.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing project data cleared.'))

        self.stdout.write(self.style.SUCCESS(f'Attempting to import data from "{csv_file_path}"'))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                # Use DictReader to read rows as dictionaries with header names as keys
                reader = csv.DictReader(csvfile)

                # --- Add this line to print the headers the script is reading ---
                self.stdout.write(f"Headers read from CSV: {reader.fieldnames}")
                # -------------------------------------------------------------

                # --- Map CSV Headers to Model Fields ---
                # IMPORTANT: These values MUST match the EXACT headers in your CSV file
                # as read by csv.DictReader.
                header_mapping = {
                    'title': 'Project Title', # Matches 'Project Title' from df.info()
                    'project_id_excel': 'ProjectID', # Matches 'ProjectID' from df.info()
                    'paas_code': 'PAAS Code', # Matches 'PAAS Code' from df.info()
                    'status': 'Approval Status', # Matches 'Approval Status' from df.info()
                    'fund': 'Fund', # Matches 'Fund' from df.info()
                    'country': 'Country(ies)', # Matches 'Country(ies)' from df.info()
                    'lead_org_unit': 'Lead Org Unit', # Matches 'Lead Org Unit' from df.info()
                    'themes': 'Theme(s)', # Matches 'Theme(s)' from df.info()
                    'donors': 'Donor(s)', # Matches 'Donor(s)' from df.info()
                    # Removed 'approval_date' mapping as it's not in df.info()
                    'start_date': 'Start Date', # Matches 'Start Date' from df.info()
                    'end_date': 'End Date', # Matches 'End Date' from df.info()
                    # Removed 'budget_amount' mapping temporarily for debugging
                    # 'budget_amount': 'Budget Amount', # Matches 'Budget Amount' from df.info()
                    'pag_value': 'PAG Value', # Matches 'PAG Value' from df.info()
                    'total_expenditure': 'Total Expenditure', # Matches 'Total Expenditure' from df.info()
                    'total_contribution': 'Total Contribution', # Matches 'Total Contribution' from df.info()
                    'total_contribution_expenditure_diff': 'Total Contribution - Total Expenditure', # Matches 'Total Contribution - Total Expenditure' from df.info()
                    'total_psc': 'Total PSC', # Matches 'Total PSC' from df.info()
                    # Add mappings for any other fields from your model if they are in the CSV
                    # 'description': 'Description', # Example if you have a Description column
                }

                # --- Validate Headers ---
                csv_headers = reader.fieldnames
                required_headers_in_csv = [
                    csv_key for model_field, csv_key in header_mapping.items()
                ]
                missing_headers = [
                     csv_key for csv_key in required_headers_in_csv
                     if csv_key not in csv_headers
                ]

                if missing_headers:
                    raise CommandError(f"Missing required CSV headers: {', '.join(missing_headers)}")

                # You might also want to check for unexpected headers if strict
                # unexpected_headers = [header for header in csv_headers if header not in header_mapping.values()]
                # if unexpected_headers:
                #     self.stdout.write(self.style.WARNING(f"Unexpected headers found: {', '.join(unexpected_headers)}"))


                imported_count = 0
                skipped_count = 0
                errors = []

                # --- Iterate through CSV rows ---
                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Access data using the mapped CSV header names
                        # Use .get() with default to avoid KeyError if header is unexpectedly missing (should be caught by validation)
                        title = row.get(header_mapping.get('title'), '').strip()
                        project_id_excel = row.get(header_mapping.get('project_id_excel'), '').strip() or None # Use None for blank
                        paas_code = row.get(header_mapping.get('paas_code'), '').strip() or None
                        status = row.get(header_mapping.get('status'), '').strip() or 'Approved' # Default status if missing or blank
                        fund = row.get(header_mapping.get('fund'), '').strip() or None
                        # description = row.get(header_mapping.get('description'), '').strip() or '' # Example for description

                        # Handle Date fields
                        # Get date strings using .get() - approval_date_str will be '' if header not mapped
                        approval_date_str = row.get(header_mapping.get('approval_date'), '').strip() # This will be '' now
                        start_date_str = row.get(header_mapping.get('start_date'), '').strip()
                        end_date_str = row.get(header_mapping.get('end_date'), '').strip()

                        # Convert date strings to Django DateField objects
                        # IMPORTANT: Adjust the date format parsing (%Y-%m-%d) based on your CSV format
                        # Pandas datetime64[ns] saved to CSV might be in ISO format or another string.
                        # Example formats: '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'
                        # Check your CSV or original dataframe output for the exact format.
                        # If dates are like '2023-10-27 00:00:00+00:00', you'll need a more complex parser or string slicing.
                        # Assuming simpleYYYY-MM-DD for now.
                        date_format = '%Y-%m-%d' # Adjust this if your CSV date format is different

                        approval_date = None
                        if approval_date_str: # This check will now correctly evaluate to False if the header wasn't mapped
                            try:
                                # Attempt to parse the date string
                                # If your dates have time/timezone, you might need to parse as datetime first
                                approval_date = timezone.datetime.strptime(approval_date_str, date_format).date()
                            except ValueError:
                                errors.append(f"Row {row_num}: Invalid approval date format '{approval_date_str}'. Expected '{date_format}'.")
                                approval_date = None # Set to None if invalid


                        start_date = None
                        if start_date_str:
                             try:
                                start_date = timezone.datetime.strptime(start_date_str, date_format).date()
                             except ValueError:
                                errors.append(f"Row {row_num}: Invalid start date format '{start_date_str}'. Expected '{date_format}'.")
                                start_date = None

                        end_date = None
                        if end_date_str:
                             try:
                                end_date = timezone.datetime.strptime(end_date_str, date_format).date()
                             except ValueError:
                                errors.append(f"Row {row_num}: Invalid end date format '{end_date_str}'. Expected '{date_format}'.")
                                end_date = None


                        # Handle Monetary (Decimal) fields
                        # Convert string to Decimal, handle potential errors
                        # Get monetary strings using .get()
                        # budget_amount_str will be '' now as header is not mapped
                        budget_amount_str = row.get(header_mapping.get('budget_amount'), '').strip()
                        pag_value_str = row.get(header_mapping.get('pag_value'), '').strip()
                        total_expenditure_str = row.get(header_mapping.get('total_expenditure'), '').strip()
                        total_contribution_str = row.get(header_mapping.get('total_contribution'), '').strip()
                        total_contribution_expenditure_diff_str = row.get(header_mapping.get('total_contribution_expenditure_diff'), '').strip()
                        total_psc_str = row.get(header_mapping.get('total_psc'), '').strip()

                        budget_amount = None
                        if budget_amount_str: # This check will now correctly evaluate to False
                            try:
                                # Remove any currency symbols or commas if present before converting
                                cleaned_amount_str = budget_amount_str.replace('$', '').replace(',', '')
                                budget_amount = Decimal(cleaned_amount_str)
                            except InvalidOperation:
                                errors.append(f"Row {row_num}: Invalid budget amount format '{budget_amount_str}'.")
                                budget_amount = None
                            except ValueError: # Catch potential errors from replace if input is not string
                                 errors.append(f"Row {row_num}: Invalid budget amount format '{budget_amount_str}'.")
                                 budget_amount = None


                        pag_value = None
                        if pag_value_str:
                            try:
                                cleaned_amount_str = pag_value_str.replace('$', '').replace(',', '')
                                pag_value = Decimal(cleaned_amount_str)
                            except InvalidOperation:
                                errors.append(f"Row {row_num}: Invalid PAG value format '{pag_value_str}'.")
                                pag_value = None
                            except ValueError:
                                 errors.append(f"Row {row_num}: Invalid PAG value format '{pag_value_str}'.")
                                 pag_value = None


                        total_expenditure = None
                        if total_expenditure_str:
                            try:
                                cleaned_amount_str = total_expenditure_str.replace('$', '').replace(',', '')
                                total_expenditure = Decimal(cleaned_amount_str)
                            except InvalidOperation:
                                errors.append(f"Row {row_num}: Invalid total expenditure format '{total_expenditure_str}'.")
                                total_expenditure = None
                            except ValueError:
                                errors.append(f"Row {row_num}: Invalid total expenditure format '{total_expenditure_str}'.")
                                total_expenditure = None

                        total_contribution = None
                        if total_contribution_str:
                            try:
                                cleaned_amount_str = total_contribution_str.replace('$', '').replace(',', '')
                                total_contribution = Decimal(cleaned_amount_str)
                            except InvalidOperation:
                                errors.append(f"Row {row_num}: Invalid total contribution format '{total_contribution_str}'.")
                                total_contribution = None
                            except ValueError:
                                errors.append(f"Row {row_num}: Invalid total contribution format '{total_contribution_str}'.")
                                total_contribution = None


                        total_contribution_expenditure_diff = None
                        if total_contribution_expenditure_diff_str:
                            try:
                                cleaned_amount_str = total_contribution_expenditure_diff_str.replace('$', '').replace(',', '')
                                total_contribution_expenditure_diff = Decimal(cleaned_amount_str)
                            except InvalidOperation:
                                errors.append(f"Row {row_num}: Invalid total contribution expenditure diff format '{total_contribution_expenditure_diff_str}'.")
                                total_contribution_expenditure_diff = None
                            except ValueError:
                                errors.append(f"Row {row_num}: Invalid total contribution expenditure diff format '{total_contribution_expenditure_diff_str}'.")
                                total_contribution_expenditure_diff = None


                        total_psc = None
                        if total_psc_str:
                            try:
                                cleaned_amount_str = total_psc_str.replace('$', '').replace(',', '')
                                total_psc = Decimal(cleaned_amount_str)
                            except InvalidOperation:
                                errors.append(f"Row {row_num}: Invalid total PSC format '{total_psc_str}'.")
                                total_psc = None
                            except ValueError:
                                errors.append(f"Row {row_num}: Invalid total PSC format '{total_psc_str}'.")
                                total_psc = None


                        # --- Handle Related Objects (Get or Create) ---
                        # For ForeignKey fields (Country, LeadOrgUnit)
                        country_name = row.get(header_mapping.get('country'), '').strip()
                        country_obj = None
                        if country_name:
                            # Get or create the Country object
                            # Using get_or_create is safe and avoids duplicates
                            country_obj, created = Country.objects.get_or_create(name=country_name)
                            if created:
                                self.stdout.write(self.style.SUCCESS(f"Created new Country: {country_name}"))


                        lead_org_unit_name = row.get(header_mapping.get('lead_org_unit'), '').strip()
                        lead_org_unit_obj = None
                        if lead_org_unit_name:
                            lead_org_unit_obj, created = LeadOrgUnit.objects.get_or_create(name=lead_org_unit_name)
                            if created:
                                self.stdout.write(self.style.SUCCESS(f"Created new Lead Org Unit: {lead_org_unit_name}"))


                        # For ManyToMany fields (Themes, Donors)
                        # Split comma-separated names and get/create objects
                        themes_string = row.get(header_mapping.get('themes'), '').strip()
                        theme_objects = []
                        if themes_string:
                            # Split by comma, strip whitespace, filter out empty strings
                            theme_names = [name.strip() for name in themes_string.split(',') if name.strip()]
                            for theme_name in theme_names:
                                theme_obj, created = Theme.objects.get_or_create(name=theme_name)
                                if created:
                                    self.stdout.write(self.style.SUCCESS(f"Created new Theme: {theme_name}"))
                                theme_objects.append(theme_obj)


                        donors_string = row.get(header_mapping.get('donors'), '').strip()
                        donor_objects = []
                        if donors_string:
                            # Split by comma, strip whitespace, filter out empty strings
                            donor_names = [name.strip() for name in donors_string.split(',') if name.strip()]
                            for donor_name in donor_names:
                                donor_obj, created = Donor.objects.get_or_create(name=donor_name)
                                if created:
                                    self.stdout.write(self.style.SUCCESS(f"Created new Donor: {donor_name}"))
                                donor_objects.append(donor_obj)


                        # --- Create or Update Project Instance ---
                        # Use update_or_create based on project_id_excel if it exists, otherwise create
                        # Check if project_id_excel is not None and not an empty string after stripping
                        lookup_project_id_excel = project_id_excel if project_id_excel else None

                        if not title:
                            errors.append(f"Row {row_num}: Skipping project due to missing title.")
                            skipped_count += 1
                            continue # Skip this row if title is missing

                        # Prepare data dictionary for Project instance
                        project_data = {
                            'title': title,
                            'project_id_excel': lookup_project_id_excel, # Use the cleaned ID for data
                            'paas_code': paas_code,
                            'status': status,
                            'fund': fund,
                            'country': country_obj, # Assign the Country object or None
                            'lead_org_unit': lead_org_unit_obj, # Assign the LeadOrgUnit object or None
                            'approval_date': approval_date, # This will be None if the column wasn't in CSV
                            'start_date': start_date,
                            'end_date': end_date,
                            'budget_amount': budget_amount, # This will be None now
                            'pag_value': pag_value,
                            'total_expenditure': total_expenditure,
                            'total_contribution': total_contribution,
                            'total_contribution_expenditure_diff': total_contribution_expenditure_diff,
                            'total_psc': total_psc,
                            # created_at and updated_at are auto-handled
                        }

                        # Use update_or_create if project_id_excel is available for lookup
                        if lookup_project_id_excel:
                            project_instance, created = Project.objects.update_or_create(
                                project_id_excel=lookup_project_id_excel, # Lookup based on cleaned excel ID
                                defaults=project_data # Data to create or update with
                            )
                            if created:
                                self.stdout.write(self.style.SUCCESS(f"Created Project: {title} (Excel ID: {lookup_project_id_excel})"))
                            else:
                                self.stdout.write(self.style.SUCCESS(f"Updated Project: {title} (Excel ID: {lookup_project_id_excel})"))
                        else:
                            # If no excel ID for lookup, just create a new project
                            project_instance = Project.objects.create(**project_data)
                            self.stdout.write(self.style.SUCCESS(f"Created Project: {title} (No Excel ID for lookup)"))


                        # --- Handle ManyToMany Relationships ---
                        # For ManyToMany fields, you need to set them *after* the instance is created/updated
                        project_instance.themes.set(theme_objects) # Use set() to replace existing themes
                        project_instance.donors.set(donor_objects) # Use set() to replace existing donors


                        imported_count += 1

                        # Optional: Save the instance if you made changes after create/update,
                        # but update_or_create with defaults usually handles this.
                        # project_instance.save()


                    except Exception as e:
                        # Catch any other unexpected errors during row processing
                        errors.append(f"Row {row_num}: Error processing row - {e}")
                        skipped_count += 1
                        # Continue processing other rows

        except FileNotFoundError:
            raise CommandError(f'CSV file not found at "{csv_file_path}"')
        except Exception as e:
            # Catch errors during file opening or DictReader initialization
            raise CommandError(f'An error occurred during CSV reading: {e}')


        self.stdout.write(self.style.SUCCESS('--- Import Summary ---'))
        self.stdout.write(self.style.SUCCESS(f'Successfully imported/updated {imported_count} projects.'))
        if skipped_count > 0:
             self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} rows due to errors.'))
        if errors:
            self.stdout.write(self.style.ERROR('--- Errors Encountered ---'))
            for error_msg in errors:
                self.stdout.write(self.style.ERROR(error_msg))
