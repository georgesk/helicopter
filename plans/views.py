from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import CHOICES_ANALOG, CHOICES_BINARY, Plan

# Create your views here.

def index(request):
    """
    page d'accueil de /plans
    """
    return render(request, "index.html",{})

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

svg.short_description="Afficher les dessins"
    
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
