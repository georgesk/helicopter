from django.shortcuts import render, HttpResponse

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
    
