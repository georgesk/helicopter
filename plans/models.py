from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import Form, ModelForm, ValidationError, Select

# Create your models here.

class Plan(models.Model):
    hauteur_helice = models.IntegerField(
        verbose_name = "Hauteur de l'hélice (mm)",
        default      = 70,
        choices      = [(n,n) for n in range(65,126)],
    )
    hauteur_habitacle = models.IntegerField(
        verbose_name = "Hauteur de l'habitacle (mm)",
        default      = 25,
        choices      = [(n,n) for n in range(10,36)],
    )
    hauteur_corps = models.IntegerField(
        verbose_name = "Hauteur du corps (mm)",
        default      = 70,
        choices      = [(n,n) for n in range(35,126)],
    )
    largeur_totale = models.IntegerField(
        verbose_name = "Largeur totale (mm)",
        default      = 50,
        choices      = [(n,n) for n in range(30,56)],
    )
    trombones = models.IntegerField(
        verbose_name = "Nombre de trombones",
        default      = 1,
        choices      = [(n,n) for n in range(1,4)],
    )
    repli = models.BooleanField(
        verbose_name = "Repli en bout d'hélice",
        default = True
    )
    corps_scotche = models.BooleanField(
        verbose_name = "Corps scotché",
        default = True
    )
    helices_scotchees = models.BooleanField(
        verbose_name = "Hélices scotchées",
        default = True
    )
    decalage_repli = models.IntegerField(
        verbose_name = "Décalage du repli (mm)",
        default      = 5,
        choices      = [(n,n) for n in range(0,21)],
    )
    angle_repli = models.IntegerField(
        verbose_name = "Angle du repli (°)",
        default      = 75,
        choices      = [(n,n) for n in range(70,111)],
    )
    couches_corps = models.IntegerField(
        verbose_name = "Corps en n couche repliées",
        default      = 1,
        choices      = [(1,1),(3,3)],
    )
    sens_rotation = models.IntegerField(
        verbose_name = "Sens de rotation",
        default      = 1,
        choices      = [(1,"horaire"),(-1,"anti-horaire")],
    )
    largeur_scotch = models.IntegerField(
        verbose_name = "Largeur de scotch (mm)",
        default      = 19,
        choices      = [(19,19)],
    )
    imprimer_symboles = models.BooleanField(
        verbose_name = "Imprimer les symboles",
        default = True,
        choices = [(True, "Oui")],
    )
