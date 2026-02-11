import requests
import time
from django.core.management.base import BaseCommand
from countries.models import Country


class Command(BaseCommand):
    help = 'Import countries data from REST Countries API'

    API_URL = 'https://restcountries.com/v3.1/all?fields=name,cca2,cca3,capital,region,subregion,population,area,flags,currencies'
    MAX_RETRIES = 3
    RETRY_DELAY = 2 # seconds
    
    def handle(self, *args, **options):
        self.stdout.write('Fetching countries from API...')
        
        for attempt in range(1, self.MAX_RETRIES+1):
            try:
                self.stdout.write(f'Attempt {attempt}/{self.MAX_RETRIES}...')
                response = requests.get(self.API_URL, timeout=30)
                response.raise_for_status()
                countries_data = response.json()
                self.stdout.write(self.style.SUCCESS(f'API request successful on attempt {attempt}'))
                break
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'API request failed: {e}'))
                if attempt < self.MAX_RETRIES:
                    self.stdout.write(f'Retrying in {self.RETRY_DELAY} seconds...')
                    time.sleep(self.RETRY_DELAY)
                else:
                    self.stdout.write(self.style.ERROR('All retry attempts failed. Aborting.'))
                    return

        self.stdout.write(f'Received {len(countries_data)} countries')
        
        created_count = 0
        updated_count = 0
        error_count = 0

        for item in countries_data:
            try:
                cca3 = item.get('cca3')
                if not cca3:
                    self.stdout.write(self.style.WARNING(f'Skipping country without cca3'))
                    error_count += 1
                    continue

                # Extraction capital (première si liste)
                capital_list = item.get('capital', [])
                capital = capital_list[0] if capital_list else None

                # Extraction flag URL
                flags = item.get('flags', {})
                flag_url = flags.get('png', '')

                # Préparation des données
                defaults = {
                    'cca2': item.get('cca2', ''),
                    'common_name': item.get('name', {}).get('common', ''),
                    'official_name': item.get('name', {}).get('official', ''),
                    'capital': capital,
                    'region': item.get('region', ''),
                    'subregion': item.get('subregion', ''),
                    'population': item.get('population', 0),
                    'area': item.get('area'),
                    'flag_url': flag_url,
                    'currencies': item.get('currencies', {}),
                }

                # Update or create (idempotent)
                country, created = Country.objects.update_or_create(
                    cca3=cca3,
                    defaults=defaults
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Error processing {item.get("cca3", "unknown")}: {e}')
                )

        # Import Completed
        self.stdout.write(self.style.SUCCESS(
            f'\nImport completed:\n'
            f'  - Created: {created_count}\n'
            f'  - Updated: {updated_count}\n'
            f'  - Errors: {error_count}'
        ))
