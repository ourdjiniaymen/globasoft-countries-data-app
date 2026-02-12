import requests
from django.test import TestCase, Client
from django.urls import reverse
from django.db.utils import IntegrityError
from unittest.mock import patch, Mock
from decimal import Decimal
from .models import Country
from .management.commands.import_countries import Command


class CountryModelTest(TestCase):
    """Tests pour le modèle Country"""
    
    def setUp(self):
        self.country = Country.objects.create(
            cca3='FRA',
            cca2='FR',
            common_name='France',
            official_name='French Republic',
            capital='Paris',
            region='Europe',
            subregion='Western Europe',
            population=67000000,
            area=Decimal('551695.00'),
            flag_url='https://example.com/flag.png',
            currencies={'EUR': {'name': 'Euro', 'symbol': '€'}}
        )
    
    def test_country_creation(self):
        """Test création d'un pays"""
        self.assertEqual(self.country.cca3, 'FRA')
        self.assertEqual(self.country.common_name, 'France')
        self.assertEqual(self.country.population, 67000000)
    
    def test_country_str(self):
        """Test méthode __str__"""
        self.assertEqual(str(self.country), 'France (FRA)')
    
    def test_cca3_unique(self):
        """Test unicité de cca3"""
        # Exception if Doublon
        with self.assertRaises(IntegrityError):
            Country.objects.create(
                cca3='FRA',  
                cca2='FR',
                common_name='France Duplicate',
                official_name='French Republic',
                region='Europe',
                population=1000000
            )

class ImportCountriesCommandTest(TestCase):
    """Tests pour la commande import_countries"""
    
    @patch('countries.management.commands.import_countries.requests.get')
    def test_import_success(self, mock_get):
        """Test import réussi depuis l'API"""
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'cca3': 'FRA',
                'cca2': 'FR',
                'name': {'common': 'France', 'official': 'French Republic'},
                'capital': ['Paris'],
                'region': 'Europe',
                'subregion': 'Western Europe',
                'population': 67000000,
                'area': 551695,
                'flags': {'png': 'https://example.com/flag.png'},
                'currencies': {'EUR': {'name': 'Euro', 'symbol': '€'}}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Exécution de la commande
        command = Command()
        command.handle()
        
        # Vérifications
        self.assertEqual(Country.objects.count(), 1)
        country = Country.objects.get(cca3='FRA')
        self.assertEqual(country.common_name, 'France')
        self.assertEqual(country.capital, 'Paris')
    
    @patch('countries.management.commands.import_countries.requests.get')
    def test_import_idempotent(self, mock_get):
        """Test idempotence: re-run ne crée pas de doublons"""
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'cca3': 'FRA',
                'cca2': 'FR',
                'name': {'common': 'France', 'official': 'French Republic'},
                'capital': ['Paris'],
                'region': 'Europe',
                'subregion': 'Western Europe',
                'population': 67000000,
                'area': 551695,
                'flags': {'png': 'https://example.com/flag.png'},
                'currencies': {}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Premier import
        command = Command()
        command.handle()
        self.assertEqual(Country.objects.count(), 1)
        
        # Deuxième import (même données)
        command.handle()
        self.assertEqual(Country.objects.count(), 1)  # Toujours 1, pas de doublon
    
    @patch('countries.management.commands.import_countries.requests.get')
    @patch('countries.management.commands.import_countries.time.sleep')
    def test_import_retry_on_failure(self, mock_sleep, mock_get):
        """Test retry mechanism: réussit au 2ème essai"""
        # Premier appel échoue, deuxième réussit
        mock_response_success = Mock()
        mock_response_success.json.return_value = [
            {
                'cca3': 'FRA',
                'cca2': 'FR',
                'name': {'common': 'France', 'official': 'French Republic'},
                'capital': ['Paris'],
                'region': 'Europe',
                'subregion': 'Western Europe',
                'population': 67000000,
                'area': 551695,
                'flags': {'png': 'https://example.com/flag.png'},
                'currencies': {}
            }
        ]
        mock_response_success.raise_for_status = Mock()
        
        # Premier appel lève une exception, deuxième réussit
        mock_get.side_effect = [
            requests.RequestException('Network error'),
            mock_response_success
        ]
        
        # Exécution de la commande
        command = Command()
        command.handle()
        
        # Vérifications
        self.assertEqual(mock_get.call_count, 2)  # 2 tentatives
        self.assertEqual(mock_sleep.call_count, 1)  # 1 délai entre les tentatives
        mock_sleep.assert_called_with(2)  # Délai de 2 secondes
        self.assertEqual(Country.objects.count(), 1)  # Import réussi
    
    @patch('countries.management.commands.import_countries.requests.get')
    @patch('countries.management.commands.import_countries.time.sleep')
    def test_import_all_retries_fail(self, mock_sleep, mock_get):
        """Test échec après 3 tentatives"""
        # Toutes les tentatives échouent
        mock_get.side_effect = requests.RequestException('Network error')
        
        # Exécution de la commande
        command = Command()
        command.handle()
        
        # Vérifications
        self.assertEqual(mock_get.call_count, 3)  # 3 tentatives
        self.assertEqual(mock_sleep.call_count, 2)  # 2 délais (entre tentative 1-2 et 2-3)
        self.assertEqual(Country.objects.count(), 0)  # Aucun pays importé


class CountryListViewTest(TestCase):
    """Tests pour la vue liste des pays"""
    
    def setUp(self):
        self.client = Client()
        # Création de pays de test
        Country.objects.create(
            cca3='FRA', cca2='FR', common_name='France',
            official_name='French Republic', region='Europe',
            population=67000000, area=Decimal('551695')
        )
        Country.objects.create(
            cca3='DEU', cca2='DE', common_name='Germany',
            official_name='Federal Republic of Germany', region='Europe',
            population=83000000, area=Decimal('357022')
        )
        Country.objects.create(
            cca3='USA', cca2='US', common_name='United States',
            official_name='United States of America', region='Americas',
            population=331000000, area=Decimal('9833517')
        )
    
    def test_list_view_status(self):
        """Test que la page liste est accessible"""
        response = self.client.get(reverse('countries:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'countries/list.html')
    
    def test_list_view_contains_countries(self):
        """Test que la liste contient les pays"""
        response = self.client.get(reverse('countries:list'))
        self.assertContains(response, 'France')
        self.assertContains(response, 'Germany')
        self.assertContains(response, 'United States')
    
    def test_filter_by_region(self):
        """Test filtre par région"""
        response = self.client.get(reverse('countries:list'), {'region': 'Europe'})
        self.assertContains(response, 'France')
        self.assertContains(response, 'Germany')
        self.assertNotContains(response, 'United States')
    
    def test_search_by_name(self):
        """Test recherche par nom"""
        response = self.client.get(reverse('countries:list'), {'search': 'France'})
        self.assertContains(response, 'France')
        self.assertNotContains(response, 'Germany')


class CountryDetailViewTest(TestCase):
    """Tests pour la vue détail d'un pays"""
    
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(
            cca3='FRA', cca2='FR', common_name='France',
            official_name='French Republic', capital='Paris',
            region='Europe', subregion='Western Europe',
            population=67000000, area=Decimal('551695'),
            currencies={'EUR': {'name': 'Euro', 'symbol': '€'}}
        )
    
    def test_detail_view_status(self):
        """Test que la page détail est accessible"""
        response = self.client.get(reverse('countries:detail', args=['FRA']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'countries/detail.html')
    
    def test_detail_view_content(self):
        """Test que le détail contient les bonnes infos"""
        response = self.client.get(reverse('countries:detail', args=['FRA']))
        self.assertContains(response, 'France')
        self.assertContains(response, 'French Republic')
        self.assertContains(response, 'Paris')
        self.assertContains(response, 'Europe')
    
    def test_detail_view_404(self):
        """Test 404 pour un pays inexistant"""
        response = self.client.get(reverse('countries:detail', args=['XXX']))
        self.assertEqual(response.status_code, 404)


class StatsViewTest(TestCase):
    """Tests pour la vue statistiques"""
    
    def setUp(self):
        self.client = Client()
        # Création de plusieurs pays pour les stats
        for i in range(15):
            Country.objects.create(
                cca3=f'C{i:02d}',
                cca2=f'{i:02d}',  # Format 2 caractères: 00, 01, 02, ..., 14
                common_name=f'Country {i}',
                official_name=f'Official Country {i}',
                region='Europe' if i < 10 else 'Asia',
                population=1000000 * (15 - i),  # Population décroissante
                area=Decimal(str(100000 * (15 - i)))  # Superficie décroissante
            )
    
    def test_stats_view_status(self):
        """Test que la page stats est accessible"""
        response = self.client.get(reverse('countries:stat'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'countries/stats.html')
    
    def test_stats_total_count(self):
        """Test comptage total"""
        response = self.client.get(reverse('countries:stat'))
        self.assertEqual(response.context['total_countries'], 15)
    
    def test_stats_top_population(self):
        """Test top 10 population"""
        response = self.client.get(reverse('countries:stat'))
        top_pop = response.context['top_population']
        self.assertEqual(len(top_pop), 10)
        # Le premier doit avoir la plus grande population
        self.assertEqual(top_pop[0].common_name, 'Country 0')
    
    def test_stats_top_area(self):
        """Test top 10 superficie"""
        response = self.client.get(reverse('countries:stat'))
        top_area = response.context['top_area']
        self.assertEqual(len(top_area), 10)
        # Le premier doit avoir la plus grande superficie
        self.assertEqual(top_area[0].common_name, 'Country 0')
    
    def test_stats_region_distribution(self):
        """Test répartition par région"""
        response = self.client.get(reverse('countries:stat'))
        distribution = response.context['region_distribution']
        regions = [item['region'] for item in distribution]
        # Doit avoir 2 régions
        self.assertEqual(len(regions), 2)
        self.assertIn('Europe', regions)
        self.assertIn('Asia', regions)

