from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import CHOICES_ANALOG, CHOICES_BINARY, Plan, Experience
from django.db import models

# Create your views here.

def index(request):
    """
    page d'accueil de /plans
    """
    return render(request, "index.html",{
        "LANGUAGE_CODE": request.LANGUAGE_CODE,
    })

def svg(modeladmin, request, queryset):
    """
    Montre les dessins quand on demande à les tracer
    @param modeladmin
    @param request
    @param queryset la sélection des plans à tracer
    """
    response = HttpResponse(content_type='image/svg+xml')
    response['Content-Disposition'] = 'attachment; filename="plans.svg"'
    for plan in queryset:
        response.write(plan.svg())
        break ## boucle utilisée une seule fois !!!
    return response

svg.short_description=_("Show the plans")
    
def intervalles(request):
    """
    renvoie l'intervalle analogique qui correspond à un paramètre
    de plan.
    """
    n=int(request.GET.get("analog_data",0))
    fieldname = CHOICES_ANALOG[n][1]
    field=[f for f in Plan._meta.fields if f.verbose_name==fieldname][0]
    return JsonResponse({
        "param" : fieldname,
        "min"     : field.choices[0][0],
        "max"     : field.choices[-1][0],
        "ok"      : True,
    })


def radios(request):
    """
    renvoie les libellés pour les boutons radio.
    """
    n=int(request.GET.get("binary_data",0))
    fieldname = CHOICES_BINARY[n][1]
    field=[f for f in Plan._meta.fields if f.verbose_name==fieldname][0]
    if isinstance(field, models.BooleanField):
        first="Non"
        second="Oui"
    else:
        first=field.choices[0][0]
        second=field.choices[1][0]
    return JsonResponse({
        "param" : fieldname,
        "first" : first,
        "second": second,
        "ok"    : True,
    })

def experience(request):
    """
    fabrique un PDF correspondant à une expérience
    """
    id=int(request.GET.get("id","1"))
    e=Experience.objects.get(pk=id)
    pdf=e.toPdf()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="exp.pdf"'
    response['Content-Length'] = str(len(pdf))
    response.write(pdf)
    return response

def unPlan(request):
    """
    fabrique un PDF correspondant à un plan
    """
    id=int(request.GET.get("id","1"))
    p=Plan.objects.get(pk=id)
    pdf=p.pdf()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="unPlan.pdf"'
    response['Content-Length'] = str(len(pdf))
    response.write(pdf)
    return response
