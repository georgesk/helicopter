from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import Form, ModelForm, ValidationError, Select
from django.utils import timezone
from helicopter.svg import *
from svg.path import *
import math, hashlib

# Create your models here.

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
        return "Plan object(" + ", ".join([str(getattr(self, f.name)) for f in self._meta.get_fields() if f.name.lower()!='id']) + ")"

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
            if f.name.lower()=='id':
                continue
            y+=10
            text="{} : {}".format(f.verbose_name, getattr(self, f.name))
            result.append(Text(text, x=x, y=y, size=6, textAnchor="left"))
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
            paths.append(Text(self.immatriculation(), size="2",
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
