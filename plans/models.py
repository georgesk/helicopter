from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import Form, ModelForm, ValidationError, Select

# Create your models here.

hauteur_helice_CHOICES = [(n,n) for n in range(65,126)]
class Plan(models.Model):
    hauteur_helice = models.IntegerField(
        verbose_name = "Hauteur de l'hélice (mm)",
        default      = 70,
        choices      = hauteur_helice_CHOICES,
    )

