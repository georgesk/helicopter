from django import forms
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import Form, ModelForm, ValidationError, Select
from django.utils import timezone
from django.contrib.auth.models import User
from helicopter.svg import *
from svg.path import *
import math, hashlib

class Plan(models.Model):
    version = "v1.0"
    class Meta:
        unique_together = ('hauteur_helice', 'hauteur_habitacle', 'hauteur_corps', 'largeur_totale', 'trombones', 'repli', 'corps_scotche', 'helices_scotchees', 'decalage_repli', 'angle_repli', 'couches_corps', 'sens_rotation', 'largeur_scotch', 'imprimer_symboles')
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = "Date de création du plan"
    )
    auteur = models.ForeignKey(User)
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
        choices      = [(n,n) for n in range(40,66)],
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

    def __str__(self):
        attributs = [str(getattr(self, f.name)) for f in self._meta.get_fields() if f.name.lower() not in ('id', 'experience', 'creation')]
        return "Plan object(" + ", ".join(attributs) + ")"

    @property
    def immatriculation(self):
        """
        return une chaîne de caractères immatriculant de façon unique(?)
        le plan
        """
        return self.version+" "+hashlib.md5(self.__str__().encode("utf-8")).hexdigest()

    def cartoucheSvg(self, auteur=None):
        """
        Renvoie une liste de "paths" à imprimer pour caractériser
        un plan
        """
        if not auteur: auteur="Anonyme"
        # on commence dans les marges
        x=15
        y=20
        result=[]
        result.append(Text("Auteur : {}".format(auteur), x=x, y=y, size=6, textAnchor="left"))
        for f in self._meta.get_fields():
            # inutile d'imprimer l'ID de la base de données
            if f.name.lower() in ('id', 'experience'):
                continue
            y+=10
            text="{} : {}".format(f.verbose_name, getattr(self, f.name))
            result.append(Text(text, x=x, y=y, size=6, textAnchor="left"))
        y+=10
        result.append(Text(self.immatriculation, x=x, y=y, size=6, textAnchor="left"))
        y+=30
        result.append(Text("NOTES MANUSCRITES", x=x, y=y, size=6, textAnchor="left"))
        return result
    
    def svg(self):
        """
        Fabrique le code d'un objet SVG représentant l'hélicoptère
        @return une chaîne de caractères
        """
        ## origine au centre de la feuille, mais un peu décalée
        ## pour faire de la place au cartouche des paramètres
        xo, yo = 210/2+50, 297/2-40
        ## liste de chemins à tracer
        paths=[] 
        ## Partie droite de l'hélice
        x0, y0 = xo, yo
        x1, y1 = xo+self.largeur_totale/2, yo
        x2, y2 = xo+self.largeur_totale/2, yo-self.hauteur_helice
        x3, y3 = xo, yo-self.hauteur_helice
        paths.append(Path(
            Line(complex(x0,y0), complex(x1,y1)),
            Line(complex(x1,y1), complex(x2,y2)),
            Line(complex(x2,y2), complex(x3,y3)),
            Line(complex(x3,y3), complex(x0,y0))
        ))
        ## Partie gauche de l'hélice
        x0, y0 = xo, yo
        x1, y1 = xo-self.largeur_totale/2, yo
        x2, y2 = xo-self.largeur_totale/2, yo-self.hauteur_helice
        x3, y3 = xo, yo-self.hauteur_helice
        paths.append(Path(
            Line(complex(x0,y0), complex(x1,y1)),
            Line(complex(x1,y1), complex(x2,y2)),
            Line(complex(x2,y2), complex(x3,y3)),
            Line(complex(x3,y3), complex(x0,y0))
        ))
        ## habitacle de l'hélicoptère
        x0, y0 = xo-self.largeur_totale/2, yo
        x1, y1 = xo+self.largeur_totale/2, yo
        x2, y2 = xo+self.largeur_totale/2, yo+self.hauteur_habitacle
        x3, y3 = xo-self.largeur_totale/2, yo+self.hauteur_habitacle
        paths.append(Path(
            Line(complex(x0,y0), complex(x1,y1)),
            Line(complex(x1,y1), complex(x2,y2)),
            Line(complex(x2,y2), complex(x3,y3)),
            Line(complex(x3,y3), complex(x0,y0))
        ))
        ## corps de l'hélicoptère
        x0, y0 = xo-self.largeur_totale/2, yo+self.hauteur_habitacle
        x1, y1 = xo+self.largeur_totale/2, yo+self.hauteur_habitacle
        x2, y2 = xo+self.largeur_totale/2, yo+self.hauteur_habitacle+self.hauteur_corps
        x3, y3 = xo-self.largeur_totale/2, yo+self.hauteur_habitacle+self.hauteur_corps
        paths.append(Path(
            Line(complex(x0,y0), complex(x1,y1)),
            Line(complex(x1,y1), complex(x2,y2)),
            Line(complex(x2,y2), complex(x3,y3)),
            Line(complex(x3,y3), complex(x0,y0))
        ))
        if self.repli:
            angleRadian=math.pi*(90-self.angle_repli)/180
            ## le pli de droite
            x0, y0 = xo+self.largeur_totale/2, yo-self.hauteur_helice+self.decalage_repli
            x1, y1 = xo, y0+self.largeur_totale/2*math.tan(angleRadian)
            ## examine le cas où la ligne sort de la pale
            ok=False
            if y1 < y0:
                x1, y1 = x0+self.decalage_repli*math.tan(math.pi/2-angleRadian), yo-self.hauteur_helice
                if x1 >= xo:
                    ok=True
                else:
                    ok=False
            else:
                ok=True
            if ok:
                paths.append(Path(
                    Line(complex(x0,y0), complex(x1,y1))
                ))
            ## le pli de gauche
            x0, y0 = xo-self.largeur_totale/2, yo-self.hauteur_helice+self.decalage_repli
            x1, y1 = xo, y0+self.largeur_totale/2*math.tan(angleRadian)
            ## examine le cas où la ligne sort de la pale
            ok=False
            if y1 < y0:
                x1, y1 = x0-self.decalage_repli*math.tan(math.pi/2-angleRadian), yo-self.hauteur_helice
                if x1 <= xo:
                    ok=True
                else:
                    ok=False
            else:
                ok=True
            if ok:
                paths.append(Path(
                    Line(complex(x0,y0), complex(x1,y1))
                ))
        ## hachures et pointillés sur le corps
        #### pointillés et tirets
        x0, y0 = xo-self.largeur_totale/6, yo+self.hauteur_habitacle
        x1, y1 = xo-self.largeur_totale/6, yo+self.hauteur_habitacle+self.hauteur_corps
        paths.append((Path(Line(complex(x0,y0), complex(x1,y1))), "tiret"))
        x0, y0 = xo+self.largeur_totale/6, yo+self.hauteur_habitacle
        x1, y1 = xo+self.largeur_totale/6, yo+self.hauteur_habitacle+self.hauteur_corps
        paths.append((Path(Line(complex(x0,y0), complex(x1,y1))), "tiret"))
        if self.corps_scotche:
            x0, y0 = xo-self.largeur_scotch/2, yo+self.hauteur_habitacle
            x1, y1 = xo-self.largeur_scotch/2, yo+self.hauteur_habitacle+self.hauteur_corps
            paths.append((Path(Line(complex(x0,y0), complex(x1,y1))), "pointille"))
            x0, y0 = xo+self.largeur_scotch/2, yo+self.hauteur_habitacle
            x1, y1 = xo+self.largeur_scotch/2, yo+self.hauteur_habitacle+self.hauteur_corps
            paths.append((Path(Line(complex(x0,y0), complex(x1,y1))), "pointille"))
        if self.helices_scotchees:
            x0, y0 = xo+self.largeur_totale/4+self.largeur_scotch/2, yo
            x1, y1 = xo+self.largeur_totale/4+self.largeur_scotch/2, yo-self.hauteur_helice
            paths.append((Path(Line(complex(x0,y0), complex(x1,y1))), "pointille"))
            x0, y0 = xo+self.largeur_totale/4-self.largeur_scotch/2, yo
            x1, y1 = xo+self.largeur_totale/4-self.largeur_scotch/2, yo-self.hauteur_helice
            paths.append((Path(Line(complex(x0,y0), complex(x1,y1))), "pointille"))
            x0, y0 = xo-self.largeur_totale/4+self.largeur_scotch/2, yo
            x1, y1 = xo-self.largeur_totale/4+self.largeur_scotch/2, yo-self.hauteur_helice
            paths.append((Path(Line(complex(x0,y0), complex(x1,y1))), "pointille"))
            x0, y0 = xo-self.largeur_totale/4-self.largeur_scotch/2, yo
            x1, y1 = xo-self.largeur_totale/4-self.largeur_scotch/2, yo-self.hauteur_helice
            paths.append((Path(Line(complex(x0,y0), complex(x1,y1))), "pointille"))
           
        #### hachures
        if self.couches_corps==1:
            x0, y0 = xo-self.largeur_totale/6, yo+self.hauteur_habitacle
            x1, y1 = xo-self.largeur_totale/6, yo+self.hauteur_habitacle+self.hauteur_corps
            x2, y2 = xo-self.largeur_totale/2, yo+self.hauteur_habitacle+self.hauteur_corps
            x3, y3 = xo-self.largeur_totale/2, yo+self.hauteur_habitacle
            paths.append((Path(
                Line(complex(x0,y0), complex(x1,y1)),
                Line(complex(x1,y1), complex(x2,y2)),
                Line(complex(x2,y2), complex(x3,y3)),
                Line(complex(x3,y3), complex(x0,y0))
            ), "hachure"))
            x0, y0 = xo+self.largeur_totale/6, yo+self.hauteur_habitacle
            x1, y1 = xo+self.largeur_totale/6, yo+self.hauteur_habitacle+self.hauteur_corps
            x2, y2 = xo+self.largeur_totale/2, yo+self.hauteur_habitacle+self.hauteur_corps
            x3, y3 = xo+self.largeur_totale/2, yo+self.hauteur_habitacle
            paths.append((Path(
                Line(complex(x0,y0), complex(x1,y1)),
                Line(complex(x1,y1), complex(x2,y2)),
                Line(complex(x2,y2), complex(x3,y3)),
                Line(complex(x3,y3), complex(x0,y0))
            ), "hachure"))
        # marquages par du texte
        if self.imprimer_symboles:
            # habitacle
            paths.append(Text("Habitacle de l'hélicoptère", size="3.5",
                              x=xo, y=yo+self.hauteur_habitacle/2))
            paths.append(Text(self.immatriculation, size="2",
                              x=xo, y=yo+self.hauteur_habitacle/2+6))
            #trombone
            paths.append(Text("📎:{}".format(self.trombones), size="10", x=xo,
                              y=yo+self.hauteur_habitacle+self.hauteur_corps-2))
            # découper les zone hachurées
            if self.couches_corps==1:
                paths.append(Text("zone à découper", size="3.5", rotate=90,
                                  x=xo-self.largeur_totale/3,
                                  y=yo+self.hauteur_habitacle+self.hauteur_corps/2))
                paths.append(Text("zone à découper", size="3.5", rotate=90,
                                  x=xo+self.largeur_totale/3,
                                  y=yo+self.hauteur_habitacle+self.hauteur_corps/2))
            # Signes de pliage selon la chiralité
            texteRotation={1: "horaire", -1: "anti-horaire"}
            paths.append(Text(texteRotation[self.sens_rotation], size="3.5",
                              x=xo+self.sens_rotation*self.largeur_totale/4,
                              y=yo-5))
            paths.append(Text(texteRotation[self.sens_rotation], size="3.5",
                              x=xo-self.sens_rotation*self.largeur_totale/4,
                              y=yo-5))
            paths.append(Text("⇧", size=20,
                              x=xo+self.sens_rotation*self.largeur_totale/4,
                              y=yo-10))
            paths.append(Text("⇩", size=20,
                              x=xo-self.sens_rotation*self.largeur_totale/4,
                              y=yo-10))
        # mention des scotchs à coller
        if self.corps_scotche:
            paths.append(Text("scotch", size=5, rotate=90,
                              x=xo,
                              y=yo+self.hauteur_habitacle+self.hauteur_corps/2))
        if self.helices_scotchees:
            paths.append(Text("scotch", size=5, rotate=90,
                              x=xo+self.largeur_totale/4,
                              y=yo-self.hauteur_helice/2))
            paths.append(Text("scotch", size=5, rotate=90,
                              x=xo-self.largeur_totale/4,
                              y=yo-self.hauteur_helice/2))
        return toSvg(paths+self.cartoucheSvg())

    def saveSvg(self, filename="/tmp/helicoptere.svg"):
        """
        Enregistre au format SVG
        @param filename un nom de fichier où écrire les données
        """
        with open(filemname,"w") as out:
            out.write(self.svg())


PROFIL_CHOIX = ((0,"non inscrit"),(1,"élève atelier"),(2,"prof atelier"))
class Profil(models.Model):
    user   = models.OneToOneField(User)
    statut = models.IntegerField(
        default      = 0,
        choices      = PROFIL_CHOIX,
    )

    def __str__(self):
        return "Profil de {} : {}".format(self.user, self.verbose_statut())
    
    def verbose_statut(self):
        return [p[1] for p in PROFIL_CHOIX if p[0]==self.statut][0]

CHOICES_ANALOG = list(enumerate([f.verbose_name for f in Plan._meta.fields if isinstance(f, models.IntegerField) and len(f.choices)>2]))

CHOICES_BINARY = list(enumerate([f.verbose_name for f in Plan._meta.fields if isinstance(f, models.BooleanField) and f.name!="imprimer_symboles"]+
                               [f.verbose_name for f in Plan._meta.fields if isinstance(f, models.IntegerField) and len(f.choices)==2]))

class variationAA(models.Model):
    """
    Décrit une variation systématique de deux paramètres "analogiques"
    dont un prendra 3 valeurs différentes et l'autre 4 valeurs différentes,
    d'où la possibilité d'imprimer 12 plans différents.
    """
    class Meta:
        verbose_name = "variation analogique/analogique"
        verbose_name_plural = "variations analogique/analogique"

    auteur   = models.ForeignKey(User)
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = "Date de création de la variation"
    )
    param1 = models.IntegerField(
        verbose_name = "paramètre analogique 1",
        default      = 0,
        choices      = CHOICES_ANALOG,
    )
    param2 = models.IntegerField(
        verbose_name = "paramètre analogique 2",
        default      = 0,
        choices      = CHOICES_ANALOG,
    )
    val11 =  models.IntegerField(
        verbose_name = "valeur 1 (1)",
    )
    val12 =  models.IntegerField(
        verbose_name = "valeur 1 (2)",
    )
    val13 =  models.IntegerField(
        verbose_name = "valeur 1 (3)",
    )
    val21 =  models.IntegerField(
        verbose_name = "valeur 2 (1)",
    )
    val22 =  models.IntegerField(
        verbose_name = "valeur 2 (2)",
    )
    val23 =  models.IntegerField(
        verbose_name = "valeur 2 (3)",
    )
    val24 =  models.IntegerField(
        verbose_name = "valeur 2 (4)",
    )

    @property
    def param1_name(self):
        return CHOICES_ANALOG[self.param1][1]
    @property
    def param2_name(self):
        return CHOICES_ANALOG[self.param2][1]
    @property
    def hash(self):
        """
        return une chaîne de caractères immatriculant de façon unique(?)
        """
        return hashlib.md5(self.__str__().encode("utf-8")).hexdigest()
    
    def __str__(self):
        dico=self.__dict__
        dico["au"]=self.auteur
        return "Variation AA ({au}) [{param1}={val11},{val12},{val13}],[{param2}={val21},{val22},{val23},{val24}])".format(**dico)


class variationBA(models.Model):
    """
    Décrit une variation systématique de deux paramètres "binaires"
    et un paramètre analogique qui prendra 3 valeurs différentes.
    d'où la possibilité d'imprimer 12 plans différents.
    """
    class Meta:
        verbose_name = "variation binaire/analogique"
        verbose_name_plural = "variations binaire/analogique"

    auteur   = models.ForeignKey(User)
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = "Date de création de la variation"
    )
    param1 = models.IntegerField(
        verbose_name = "paramètre binaire 1",
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param2 = models.IntegerField(
        verbose_name = "paramètre binaire 2",
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param3 = models.IntegerField(
        verbose_name = "paramètre analogique",
        default      = 0,
        choices      = CHOICES_ANALOG,
    )
    val31 =  models.IntegerField(
        verbose_name = "valeur 3 (1)",
    )
    val32 =  models.IntegerField(
        verbose_name = "valeur 3 (3)",
    )
    val33 =  models.IntegerField(
        verbose_name = "valeur 3 (3)",
    )

    @property
    def param1_name(self):
        return CHOICES_BINARY[self.param1][1]
    @property
    def param2_name(self):
        return CHOICES_BINARY[self.param2][1]
    @property
    def param3_name(self):
        return CHOICES_ANALOG[self.param3][1]
    @property
    def hash(self):
        """
        return une chaîne de caractères immatriculant de façon unique(?)
        """
        return hashlib.md5(self.__str__().encode("utf-8")).hexdigest()
    
    def __str__(self):
        dico=self.__dict__
        dico["au"]=self.auteur
        return "Variation BA ({au}) {param1},{param2},{param3}=[{val31},{val32},{val33},])".format(**dico)

class variationBB(models.Model):
    """
    Décrit une variation systématique de cinq paramètres "binaires",
    en un groupe de trois et un groupe de deux.
    d'où la possibilité d'imprimer 12 plans différents.
    """
    class Meta:
        verbose_name = "variation binaire/binaire"
        verbose_name_plural = "variations binaire/binaire"

    auteur   = models.ForeignKey(User)
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = "Date de création de la variation"
    )
    param11 = models.IntegerField(
        verbose_name = "premier paramètre du premier groupe",
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param12 = models.IntegerField(
        verbose_name = "deuxième paramètre du premier groupe",
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param13 = models.IntegerField(
        verbose_name = "troisième paramètre du premier groupe",
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param21 = models.IntegerField(
        verbose_name = "premier paramètre du deuxième groupe",
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param22 = models.IntegerField(
        verbose_name = "deuxième paramètre du deuxième groupe",
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    
    @property
    def param11_name(self):
        return CHOICES_BINARY[self.param11][1]
    @property
    def param12_name(self):
        return CHOICES_BINARY[self.param12][1]
    @property
    def param13_name(self):
        return CHOICES_BINARY[self.param13][1]
    @property
    def param21_name(self):
        return CHOICES_BINARY[self.param21][1]
    @property
    def param22_name(self):
        return CHOICES_BINARY[self.param22][1]
    @property
    def hash(self):
        """
        return une chaîne de caractères immatriculant de façon unique(?)
        """
        return hashlib.md5(self.__str__().encode("utf-8")).hexdigest()

    def __str__(self):
        dico=self.__dict__
        dico["au"]=self.auteur
        return "Variation BB ({au}) {param11},{param12},{param13},{param21},{param22}".format(**dico)

    def clean(self):
        if len(set((self.param11,self.param12,self.param13,self.param21,self.param22))) < 5:
            raise forms.ValidationError("Les paramètres binaires choisis doivent tous être différents !")


class Experience(models.Model):
    """
    Une expérience, c'est un plan "de base", associé à une variation
    à choisir parmi une variation analogique/analogique, ou
    analogique/binaire, ou binaire/binaire. Celle-ci permet dans tous les
    cas d'imprimer 12 plans.
    .
    Une expérience est associée à un auteur et une date de conception.
    """
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = "Date de création de l'expérience"
    )
    auteur = models.ForeignKey(User)
    plan   = models.ForeignKey(Plan)
    var1   = models.ForeignKey(variationAA,
                               blank=True, null=True, default=None,
                               verbose_name="variantes analogique/analogique",
    )
    var2   = models.ForeignKey(variationBA,
                               blank=True, null=True, default=None,
                               verbose_name="variantes binaire/analogique",
    )
    var3   = models.ForeignKey(variationBB,
                               blank=True, null=True, default=None,
                               verbose_name="variantes binaire/binaire",
    )
    
    
    def clean(self, *args, **kwargs):
        """
        On vérifie qu'une et une seule des clés var1, var2, var3 est
        définie
        """
        error=""
        var=list(set((self.var1, self.var2, self.var3)))
        if len(var)==1:
            error="Il faut définir au moins une variation !"
        if len(var)>2 or None not in var:
            error="Il faut définir au plus une variation !"
        if error:
            raise forms.ValidationError(error)
        super(Experience, self).clean(*args, **kwargs)
        
    def __str__(self):
        dico=self.__dict__
        dico["au"]=self.auteur
        return "Experience({}, {}, {}, {}, {})".format(self.auteur, self.plan, self.var1, self.var2, self.var3)
