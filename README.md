# Countries Data App (Django)

Mini application Django permettant d’importer, stocker et analyser des données pays 
depuis l’API REST Countries, en utilisant exclusivement une base de données locale.

⚠️ Important : L’interface web ne fait aucun appel direct à l’API externe.  
Toutes les pages s’appuient uniquement sur les données stockées en base.

---

## Stack technique

- Python 3.10+
- Django
- SQLite (par défaut)
- Templates Django
- requests (pour l’ingestion API)

---

## Installation

```bash
git clone <repo_url>
cd <repo_name>

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Créer un fichier `.env` :

```bash
cp .env.example .env
```

---

## Lancer le projet

⚠️ Le projet Django se trouve dans le dossier `config`.

```bash
cd config
python manage.py migrate
python manage.py runserver
```

Accès :
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Import des données

```bash
cd config
python manage.py import_countries
```

La commande est idempotente :
Relancer l’import ne crée pas de doublons.

---

## Pages disponibles

* `/countries/` → Liste paginée des pays
* `/countries/<cca3>/` → Détail d’un pays
* `/stats/` → Statistiques métier

---

## Bonus (si implémentés)

* Retry API
* Tests unitaires
* Dockerisation

---

## Démonstration

Lien vidéo (à ajouter après enregistrement)

---

## Auteur

Aymen Ourdjini

```
