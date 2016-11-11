from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import Form, ModelForm, ValidationError, Select
from django.utils import timezone
from django.contrib.auth.models import User
from helicopter.svg import *
from svg.path import *
import math, hashlib, tempfile, os.path
from subprocess import call

class Plan(models.Model):
    version = "v1.0"
    class Meta:
        unique_together = ('hauteur_helice', 'hauteur_habitacle', 'hauteur_corps', 'largeur_totale', 'trombones', 'repli', 'corps_scotche', 'helices_scotchees', 'decalage_repli', 'angle_repli', 'couches_corps', 'sens_rotation', 'largeur_scotch', 'imprimer_symboles')
        verbose_name = _("plan")
        verbose_name_plural = _("plans")
        
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = _("Plan's creation date")
    )
    auteur = models.ForeignKey(User)
    hauteur_helice = models.IntegerField(
        verbose_name = _("Propellor's height (mm)"),
        default      = 70,
        choices      = [(n,n) for n in range(65,126)],
    )
    hauteur_habitacle = models.IntegerField(
        verbose_name = _("Cabin's height (mm)"),
        default      = 25,
        choices      = [(n,n) for n in range(10,36)],
    )
    hauteur_corps = models.IntegerField(
        verbose_name = _("Body's height (mm)"),
        default      = 70,
        choices      = [(n,n) for n in range(35,126)],
    )
    largeur_totale = models.IntegerField(
        verbose_name = _("Total width (mm)"),
        default      = 50,
        choices      = [(n,n) for n in range(40,66)],
    )
    trombones = models.IntegerField(
        verbose_name = _("Number of paper clips"),
        default      = 1,
        choices      = [(n,n) for n in range(1,4)],
    )
    repli = models.BooleanField(
        verbose_name = _("Fold the propellor's extremity"),
        default = True
    )
    corps_scotche = models.BooleanField(
        verbose_name = _("Taped body"),
        default = True
    )
    helices_scotchees = models.BooleanField(
        verbose_name = _("Taped propellor"),
        default = True
    )
    decalage_repli = models.IntegerField(
        verbose_name = _("Folding's offset (mm)"),
        default      = 5,
        choices      = [(n,n) for n in range(0,21)],
    )
    angle_repli = models.IntegerField(
        verbose_name = _("Folding's angle (degree)"),
        default      = 75,
        choices      = [(n,n) for n in range(70,111)],
    )
    couches_corps = models.IntegerField(
        verbose_name = _("Body layers"),
        default      = 1,
        choices      = [(1,1),(3,3)],
    )
    sens_rotation = models.IntegerField(
        verbose_name = _("Rotation sense"),
        default      = 1,
        choices      = [(1,_("clockwise")),(-1,_("counterclockwise"))],
    )
    largeur_scotch = models.IntegerField(
        verbose_name = _("Adhesive tape width (mm)"),
        default      = 19,
        choices      = [(19,19)],
    )
    imprimer_symboles = models.BooleanField(
        verbose_name = _("Print symbols"),
        default = True,
        choices = [(True, _("Yes"))],
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
        if not auteur: auteur="Anonymous"
        # on commence dans les marges
        x=15
        y=20
        result=[]
        result.append(Text(self.immatriculation, x=x, y=y, size=6, textAnchor="left"))
        for f in self._meta.get_fields():
            # inutile d'imprimer l'ID de la base de données
            if f.name.lower() in ('id', 'experience'):
                continue
            y+=7
            text="{} : {}".format(f.verbose_name, getattr(self, f.name))
            result.append(Text(text, x=x, y=y, size=6, textAnchor="left"))
        y+=7
        result.append(Text(_("Author: {}").format(auteur), x=x, y=y, size=6, textAnchor="left"))
        y+=30
        result.append(Text(_("HANDWRITTEN NOTES"), x=x, y=y, size=6, textAnchor="left"))
        return result

    def pdf(self):
        """
        Fabrique un objet pafe PDF dans un flux binaire
        """
        with tempfile.TemporaryDirectory(prefix='plan-') as tempdir:
            svgName=os.path.join(tempdir, "plan.svg")
            outfile=open(svgName,"w", encoding="utf-8")
            outfile.write(self.svg())
            outfile.close()
            pdfName=os.path.join(tempdir, "plan.pdf")
            # on le convertir vers PDF avec Inkscape
            cmd="inkscape -f {} --export-pdf {}".format(svgName, pdfName)
            call(cmd, shell=True)
            # on récupère ça sous forme de flux d'octets
            result=open("{0}/plan.pdf".format(tempdir),"rb").read()
            # on efface tout dans le dossier temporaire
            cmd="rm {}/*".format(tempdir)
            call(cmd, shell=True)
            # on renvoie le flux PDF
            return result
            
    def svg(self):
        """
        Fabrique le code d'un objet SVG représentant l'hélicoptère
        @return une chaîne de caractères
        """
        ## origine au centre de la feuille, mais un peu décalée
        ## pour faire de la place au cartouche des paramètres
        xo, yo = 210/2+50, 297/2+15
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
            paths.append(Text(_("Cabin"), size="3.5",
                              x=xo, y=yo+self.hauteur_habitacle/2))
            paths.append(Text(self.immatriculation, size="1.7",
                              x=xo, y=yo+self.hauteur_habitacle/2+4))
            #trombone
            paths.append(Text("📎:{}".format(self.trombones), size="10", x=xo,
                              y=yo+self.hauteur_habitacle+self.hauteur_corps-2))
            # découper les zone hachurées
            if self.couches_corps==1:
                paths.append(Text(_("Cut off this area"), size="3.5", rotate=90,
                                  x=xo-self.largeur_totale/3,
                                  y=yo+self.hauteur_habitacle+self.hauteur_corps/2))
                paths.append(Text(_("Cut off this area"), size="3.5", rotate=90,
                                  x=xo+self.largeur_totale/3,
                                  y=yo+self.hauteur_habitacle+self.hauteur_corps/2))
            else:
                paths.append(Text(_("Fold this area"), size="3.5", rotate=90,
                                  x=xo-self.largeur_totale/3,
                                  y=yo+self.hauteur_habitacle+self.hauteur_corps/2))
                paths.append(Text(_("Fold this area"), size="3.5", rotate=90,
                                  x=xo+self.largeur_totale/3,
                                  y=yo+self.hauteur_habitacle+self.hauteur_corps/2))
            # Signes de pliage selon la chiralité
            texteRotation={1: _("clockwise"), -1: _("counterclockwise")}
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
            paths.append(Text(_("Tape"), size=5, rotate=90,
                              x=xo,
                              y=yo+self.hauteur_habitacle+self.hauteur_corps/2))
        if self.helices_scotchees:
            paths.append(Text(_("Tape"), size=5, rotate=90,
                              x=xo+self.largeur_totale/4,
                              y=yo-self.hauteur_helice/2))
            paths.append(Text(_("Tape"), size=5, rotate=90,
                              x=xo-self.largeur_totale/4,
                              y=yo-self.hauteur_helice/2))
        return toSvg(paths+self.cartoucheSvg())

    def saveSvg(self, filename=_("/tmp/helicopter.svg")):
        """
        Enregistre au format SVG
        @param filename un nom de fichier où écrire les données
        """
        with open(filemname,"w", encoding="utf-8") as out:
            out.write(self.svg())


PROFIL_CHOIX = ((0,_("unsubscribed")),(1,_("workshop's student")),(2,_("workshop's teacher")))
class Profil(models.Model):

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        
    user   = models.OneToOneField(User)
    statut = models.IntegerField(
        default      = 0,
        choices      = PROFIL_CHOIX,
    )

    def __str__(self):
        return _("Profile of {user}: {status}").format(user=self.user,
                                                       status=self.verbose_statut())
    
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
        verbose_name = _("analog/analog variation")
        verbose_name_plural = _("analog/analog variations")

    auteur   = models.ForeignKey(User)
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = _("Variation's creation date")
    )
    param1 = models.IntegerField(
        verbose_name = _("analog parameter #1"),
        default      = 0,
        choices      = CHOICES_ANALOG,
    )
    param2 = models.IntegerField(
        verbose_name = _("analog parameter #2"),
        default      = 0,
        choices      = CHOICES_ANALOG,
    )
    val11 =  models.IntegerField(
        verbose_name = _("value #1 (1)"),
    )
    val12 =  models.IntegerField(
        verbose_name = _("value #1 (2)"),
    )
    val13 =  models.IntegerField(
        verbose_name = _("value #1 (3)"),
    )
    val21 =  models.IntegerField(
        verbose_name = _("value #2 (1)"),
    )
    val22 =  models.IntegerField(
        verbose_name = _("value #2 (2)"),
    )
    val23 =  models.IntegerField(
        verbose_name = _("value #2 (3)"),
    )
    val24 =  models.IntegerField(
        verbose_name = _("value #2 (4)"),
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
        return _("A/A Variation ({au}) [{param1}={val11},{val12},{val13}],[{param2}={val21},{val22},{val23},{val24}])").format(**dico)


class variationBA(models.Model):
    """
    Décrit une variation systématique de deux paramètres "binaires"
    et un paramètre analogique qui prendra 3 valeurs différentes.
    d'où la possibilité d'imprimer 12 plans différents.
    """
    class Meta:
        verbose_name = _("digital/analog variation")
        verbose_name_plural = _("digital/analog variations")

    auteur   = models.ForeignKey(User)
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = _("Variation's creation date")
    )
    param1 = models.IntegerField(
        verbose_name = _("Digital parameter #1"),
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param2 = models.IntegerField(
        verbose_name = _("Digital parameter #2"),
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param3 = models.IntegerField(
        verbose_name = _("Analog parameter"),
        default      = 0,
        choices      = CHOICES_ANALOG,
    )
    val31 =  models.IntegerField(
        verbose_name = _("value #3 (1)"),
    )
    val32 =  models.IntegerField(
        verbose_name = _("value #3 (3)"),
    )
    val33 =  models.IntegerField(
        verbose_name = _("value #3 (3)"),
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
        return _("D/A Variation ({au}) {param1},{param2},{param3}=[{val31},{val32},{val33},])").format(**dico)

class variationBB(models.Model):
    """
    Décrit une variation systématique de cinq paramètres "binaires",
    en un groupe de trois et un groupe de deux.
    d'où la possibilité d'imprimer 12 plans différents.
    """
    class Meta:
        verbose_name = _("Digital/digital variation")
        verbose_name_plural = _("Digital/digital variations")

    auteur   = models.ForeignKey(User)
    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = _("Variation's creation date")
    )
    param11 = models.IntegerField(
        verbose_name = _("First parameter of the first group"),
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param12 = models.IntegerField(
        verbose_name = _("Second parameter of the first group"),
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param13 = models.IntegerField(
        verbose_name = _("Third parameter of the first group"),
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param21 = models.IntegerField(
        verbose_name = _("First parameter of the second group"),
        default      = 0,
        choices      = CHOICES_BINARY,
    )
    param22 = models.IntegerField(
        verbose_name = _("Second parameter of the second group"),
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
        return _("D/D Variation ({au}) {param11},{param12},{param13},{param21},{param22}").format(**dico)

    def clean(self):
        if len(set((self.param11,self.param12,self.param13,self.param21,self.param22))) < 5:
            raise forms.ValidationError(_("Chosen digital parameters must all be distinct!"))


class Experience(models.Model):
    """
    Une expérience, c'est un plan "de base", associé à une variation
    à choisir parmi une variation analogique/analogique, ou
    analogique/binaire, ou binaire/binaire. Celle-ci permet dans tous les
    cas d'imprimer 12 plans.
    .
    Une expérience est associée à un auteur et une date de conception.
    """

    class Meta:
        verbose_name = _("experiment")
        verbose_name_plural = _("experiments")

    creation = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        blank=True,
        verbose_name = _("Experiment's creation date")
    )
    auteur = models.ForeignKey(User)
    plan   = models.ForeignKey(Plan)
    var1   = models.ForeignKey(variationAA,
                               blank=True, null=True, default=None,
                               verbose_name=_("analog/analog variants"),
    )
    var2   = models.ForeignKey(variationBA,
                               blank=True, null=True, default=None,
                               verbose_name=_("digital/analog variants"),
    )
    var3   = models.ForeignKey(variationBB,
                               blank=True, null=True, default=None,
                               verbose_name=_("digital/digital variants"),
    )
    
    
    def clean(self, *args, **kwargs):
        """
        On vérifie qu'une et une seule des clés var1, var2, var3 est
        définie
        """
        error=""
        var=list(set((self.var1, self.var2, self.var3)))
        if len(var)==1:
            error=_("At least one variation must be defined!")
        if len(var)>2 or None not in var:
            error=_("At most one variation must be defined!")
        if error:
            raise forms.ValidationError(error)
        super(Experience, self).clean(*args, **kwargs)
        
    def __str__(self):
        dico=self.__dict__
        dico["au"]=self.auteur
        return _("Experiment ({}, {}, {}, {}, {})").format(self.auteur, self.plan, self.var1, self.var2, self.var3)

    def toPdf(self):
        """
        Fabrique un fichier PDF de 12 pages qui correspond aux 
        douze variantes demandées.
        """
        with tempfile.TemporaryDirectory(prefix='experience-') as tempdir:
            svgDocs=[]
            if self.var1:
                ## déclinaison avec deux variables analogiques
                fieldname1=fieldOfChoiceAnalog(self.var1.param1).name
                fieldname2=fieldOfChoiceAnalog(self.var1.param2).name
                for v1 in (self.var1.val11, self.var1.val12, self.var1. val13):
                    for v2 in (self.var1.val21, self.var1.val22, self.var1.val23, self.var1.val24):
                        ## on fait une copie du plan, qu'on n'enregistrera pas
                        p=self.plan
                        p.pk=None
                        # on change p selon self.var1.param1
                        setattr(p,fieldname1, v1)
                        # on change p selon self.var1.param2
                        setattr(p,fieldname2, v2)
                        p.auteur=self.auteur
                        p.creation=self.creation
                        #on empile le document svg
                        svgDocs.append(p.svg())
            elif self.var2:
                ## déclinaison avec deux variables binaires et une analogique
                field1=fieldOfChoiceBinary(self.var2.param1)
                field2=fieldOfChoiceBinary(self.var2.param2)
                field3=fieldOfChoiceAnalog(self.var2.param3)
                val1=tupleFromBinaryField(field1)
                val2=tupleFromBinaryField(field2)
                for v1 in val1:
                    for v2 in val2:
                        for v3 in (self.var2.val31, self.var2.val32, self.var2. val33):
                            ## on fait une copie du plan
                            p=self.plan
                            p.pk=None
                            # on change p selon self.var2.param1
                            setattr(p,field1.name, v1)
                            # on change p selon self.var2.param2
                            setattr(p,field2.name, v2)
                            # on change p selon self.var2.param3
                            setattr(p,field3.name, v3)
                            p.auteur=self.auteur
                            p.creation=self.creation
                            #on empile le document svg
                            svgDocs.append(p.svg())
            elif self.var3:
                ## déclinaison avec cinq variables binaires
                field1=fieldOfChoiceBinary(self.var3.param11)
                field2=fieldOfChoiceBinary(self.var3.param12)
                field3=fieldOfChoiceBinary(self.var3.param13)
                field4=fieldOfChoiceBinary(self.var3.param21)
                field5=fieldOfChoiceBinary(self.var3.param22)
                val1=tupleFromBinaryField(field1)
                val2=tupleFromBinaryField(field2)
                val3=tupleFromBinaryField(field3)
                val4=tupleFromBinaryField(field4)
                val5=tupleFromBinaryField(field5)
                ## boucle pour les 8 premières feuilles
                for v1 in val1:
                    for v2 in val2:
                        for v3 in val3:
                            ## on fait une copie du plan
                            p=self.plan
                            p.pk=None
                            # on change p selon self.var3.param1
                            setattr(p,field1.name, v1)
                            # on change p selon self.var3.param2
                            setattr(p,field2.name, v2)
                            # on change p selon self.var3.param3
                            setattr(p,field3.name, v3)
                            p.auteur=self.auteur
                            p.creation=self.creation
                            #on empile le document svg
                            svgDocs.append(p.svg())
                ## boucle pour les 4 feuilles suivantes
                for v4 in val4:
                    for v5 in val5:
                        ## on fait une copie du plan
                        p=self.plan
                        p.pk=None
                        # on change p selon self.var3.param4
                        setattr(p,field4.name, v4)
                        # on change p selon self.var3.param5
                        setattr(p,field5.name, v5)
                        p.auteur=self.auteur
                        p.creation=self.creation
                        #on empile le document svg
                        svgDocs.append(p.svg())
            else:
                raise ValueError(_("unexpected experiment, could not make a plan!"))
            outSvgFiles=[]
            outPdfFiles=[]
            i=0
            for d in svgDocs:
                # on injecte le document svg dans un fichier temporaire
                svgName=os.path.join(tempdir, "%03d.svg" %i)
                outfile=open(svgName,"w", encoding="utf-8")
                outfile.write(d)
                outfile.close()
                pdfName=os.path.join(tempdir, "%03d.pdf" %i)
                i+=1
                # on le convertir vers PDF avec Inkscape
                cmd="inkscape -f {} --export-pdf {}".format(svgName, pdfName)
                call(cmd, shell=True)
            # on concatène toutes les pages pour former un seul PDF
            cmd="pdftk {0}/0*.pdf cat output {0}/exp.pdf".format(tempdir)
            call(cmd, shell=True)
            # on récupère ça sous forme de flux d'octets
            result=open("{0}/exp.pdf".format(tempdir),"rb").read()
            # on efface tout dans le dossier temporaire
            cmd="rm {}/*".format(tempdir)
            call(cmd, shell=True)
            # on renvoie le flux PDF
            return result
                
def fieldOfChoiceAnalog(n):
    """
    renvoie le champ de plan qui est le nième champ analogique
    """
    return [f for f in Plan._meta.get_fields() if f.name.lower() not in ('id', 'experience', 'creation') and f.verbose_name==CHOICES_ANALOG[n][1]][0]

def fieldOfChoiceBinary(n):
    """
    renvoie le champ de plan qui est le nième champ analogique
    """
    return [f for f in Plan._meta.get_fields() if f.name.lower() not in ('id', 'experience', 'creation') and f.verbose_name==CHOICES_BINARY[n][1]][0]

def tupleFromBinaryField(field):
    """
    renvoie un tuple qui correspond à un champ binaire, soit booléen,
    soit discret à deux valeurs
    """
    if isinstance(field,models.BooleanField):
        return (False, True)
    else:
        return (field.choices[0][0], field.choices[1][0])
    
