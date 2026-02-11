from django.db import models

class Country(models.Model):
   # Identifiants
    cca3 = models.CharField(max_length=3, unique=True, primary_key=True)
    cca2 = models.CharField(max_length=2, db_index=True)

    # Noms
    common_name = models.CharField(max_length=255)
    official_name = models.CharField(max_length=255)

    # Localisation
    capital = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100, db_index=True)
    subregion = models.CharField(max_length=100, blank=True, null=True)

    # Données numériques
    population = models.BigIntegerField(db_index=True)
    area = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Autres 
    flag_url = models.URLField(max_length=500, blank=True, null=True)
    currencies = models.JSONField(default=dict, blank=True)

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['common_name']
        verbose_name_plural = "Countries"

    def __str__(self):
        return f"{self.common_name} ({self.cca3})"

