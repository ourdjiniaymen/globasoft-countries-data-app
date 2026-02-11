# Countries Data App

Application Django permettant d'importer, stocker et visualiser des données sur les pays du monde depuis l'API REST Countries.

## Fonctionnalités

- Import des données pays depuis l'API REST Countries
- Stockage en base de données locale (PostgreSQL ou SQLite)
- Interface web avec:
  - Liste des pays (pagination, filtres par région, recherche)
  - Page détail de chaque pays
  - Page statistiques (top 10 population/superficie, répartition régionale)
- Mécanisme de retry automatique (3 tentatives)
- Tests unitaires complets
- Dockerisation avec PostgreSQL

## Technologies

- Python 3.11+
- Django 6.0
- PostgreSQL 15 (Docker) ou SQLite (local)
- Docker & Docker Compose
- Requests

## Prérequis

### Option 1: Installation locale
- Python 3.11+
- pip

### Option 2: Installation Docker
- Docker
- Docker Compose

## Installation

### Option 1: Installation locale (SQLite)

1. **Cloner le repository**
```bash
git clone <repository-url>
cd <project-directory>
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
# Copier le fichier exemple
copy .env.example .env  # Windows
# ou
cp .env.example .env  # Linux/Mac

# Éditer .env et supprimer les variables POSTGRES_* pour utiliser SQLite
```

5. **Appliquer les migrations**
```bash
cd config
python manage.py migrate
```

6. **Importer les données**
```bash
python manage.py import_countries
```

7. **Lancer le serveur**
```bash
python manage.py runserver
```

8. **Accéder à l'application**
```
http://127.0.0.1:8000/countries/
```

### Option 2: Installation Docker (PostgreSQL)

1. **Cloner le repository**
```bash
git clone <repository-url>
cd <project-directory>
```

2. **Configurer les variables d'environnement**
```bash
# Le fichier .env est déjà configuré pour Docker
# Vous pouvez modifier les valeurs si nécessaire
```

3. **Démarrer les containers**
```bash
docker-compose up --build
```

L'application démarre automatiquement et:
- Applique les migrations
- Import les données depuis l'API
- Lance le serveur sur http://localhost:8000

4. **Accéder à l'application**
```
http://localhost:8000/countries/
```

## URLs disponibles

- `/countries/` - Liste des pays (avec pagination, filtres, recherche)
- `/countries/<cca3>/` - Détail d'un pays (ex: /countries/FRA/)
- `/stats/` - Statistiques globales
- `/admin/` - Interface d'administration Django

## Tests

### Lancer les tests
```bash
cd config
python manage.py test countries
```

### Tests inclus
- Tests du modèle Country
- Tests de la commande import_countries (avec retry)
- Tests des vues (liste, détail, stats)
- Tests des filtres et recherche

## Commandes utiles

### Import/Re-import des données
```bash
# Local
python manage.py import_countries

# Docker
docker-compose exec web python manage.py import_countries
```

### Créer un superuser
```bash
# Local
python manage.py createsuperuser

# Docker
docker-compose exec web python manage.py createsuperuser
```

### Arrêter Docker
```bash
docker-compose down

# Avec suppression des volumes (données)
docker-compose down -v
```

## Structure du projet

```
.
├── config/                 # Projet Django
│   ├── config/            # Configuration Django
│   ├── countries/         # Application principale
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── import_countries.py
│   │   ├── templates/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── tests.py
│   └── manage.py
├── .env                   # Variables d'environnement
├── .env.example          # Template des variables
├── docker-compose.yml    # Configuration Docker
├── Dockerfile           # Image Docker
├── requirements.txt     # Dépendances Python
└── README.md           # Ce fichier
```

## Points techniques importants

- **Idempotence**: La commande `import_countries` peut être relancée sans créer de doublons (utilise `update_or_create`)
- **Retry**: 3 tentatives automatiques avec délai de 2 secondes en cas d'échec API
- **Clé unique**: Le code `cca3` est utilisé comme clé primaire
- **Pas d'appel API dans les views**: Toutes les données proviennent de la base locale
- **Fallback SQLite**: Si PostgreSQL n'est pas configuré, utilise SQLite automatiquement

## API Source

Données provenant de: https://restcountries.com/v3.1/all

## Auteur

Aymen OURDJINI

