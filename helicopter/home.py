from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import *
from plans.models import Profil, Plan, Experience, \
    variationAA, variationBA, variationBB

def checkgroups(user, subscribed=[], unsubscribed=[]):
    """
    fait le point sur les groupes où inscrire un utilisateur.
    Le drapeau is_staff sera systématiquement levé, puis
    on désinscrit de la list de groupes dont les noms sont dans unsuscribed
    et on inscrit dans les groupes dont les noms sont dans subscribed
    """
    dirty=False
    if not user.is_staff:
        user.is_staff=True
        dirty=True
    for n in unsubscribed:
        if user.groups.filter(name=n).exists():
            g=Group.objects.get(name=n)
            if g:
                g.user_set.remove(user)
    for n in subscribed:
        if not user.groups.filter(name=n).exists():
            g=Group.objects.get(name=n)
            if g:
                g.user_set.add(user)
    if dirty:
        user.save()
    return


def index(request):
    if request.user.is_authenticated():
        profils=list(Profil.objects.filter(user=request.user.pk))
        if len(profils)==0:
            # oncrée le profil nul à la volée si nécessaire
            profil=Profil(user=request.user)
            profil.save()
        else:
            profil=profils[0]
        if profil.statut==2: #professeur
            ### on vérifie que l'utilisateur appartien au groupe profs
            ### et a le statut staff
            checkgroups(request.user,subscribed=["profs"], unsubscribed=["eleves"])
            ### on affiche la liste des profs, des élèves inscrits,
            ### et des élèves visiteurs
            pProf=Profil.objects.filter(statut=2).order_by("user__last_name","user__first_name")
            pEleve=Profil.objects.filter(statut=1).order_by("user__last_name","user__first_name")
            pVisiteur=Profil.objects.filter(statut=0).order_by("user__last_name","user__first_name")
            return render(
                request,
                "home_prof.html",
                {
                    "LANGUAGE_CODE": request.LANGUAGE_CODE,
                    "profil"    : profil.verbose_statut(),
                    "profs"     : [p.user for p in pProf],
                    "eleves"    : [p.user for p in pEleve],
                    "visiteurs" : [p.user for p in pVisiteur],
                }
            )
        elif profil.statut==1: #élève
            ### on vérifie que l'utilisateur appartient au groupe eleves
            ### et a le statut staff
            checkgroups(request.user,subscribed=["eleves"], unsubscribed=["profs"])
            vaa=variationAA.objects.filter(auteur=request.user)
            vba=variationBA.objects.filter(auteur=request.user)
            vbb=variationBB.objects.filter(auteur=request.user)
            return render(
                request,
                "home_eleve.html",
                {
                    "LANGUAGE_CODE": request.LANGUAGE_CODE,
                    "profil"      : profil.verbose_statut(),
                    "plans"       : Plan.objects.filter(auteur=request.user),
                    "experiences" : Experience.objects.filter(auteur=request.user),
                    "variantesAA" : vaa,
                    "variantesBA" : vba,
                    "variantesBB" : vbb,
                    "vlength"     : len(vaa)+len(vbb)+len(vba),
                }
            )
        else: # par défaut
            return render(
                request,
                "home.html",
                {
                    "LANGUAGE_CODE": request.LANGUAGE_CODE,
                    "profil": profil.verbose_statut()
                }
            )
    else:
        return HttpResponseRedirect("/login/")


