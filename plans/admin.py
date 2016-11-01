from django.contrib import admin
from plans.models import Plan
import plans.views as views

# Register your models here.

class PlanAdmin (admin.ModelAdmin):
    class Media:
        js = (
            '/static/plans/js/jquery/jquery.js',
            '/static/plans/js/jquery-ui/jquery-ui.js',
)
        css = {
            'all': (
                '/static/plans/css/base.css',
                '/static/plans/js/jquery-ui/css/smoothness/jquery-ui.min.css',
            ),
        }
    fields = (
        ('hauteur_helice','hauteur_habitacle','hauteur_corps',),
        ('largeur_totale', 'trombones','couches_corps',),
        ('corps_scotche','helices_scotchees','largeur_scotch',),
        ('repli','decalage_repli','angle_repli',),
        ('sens_rotation','imprimer_symboles',),
    )
    
    list_display = (
        'creation',
        'hauteur_helice','hauteur_habitacle','hauteur_corps',
        'largeur_totale', 'trombones','couches_corps',
        'corps_scotche','helices_scotchees','largeur_scotch',
        'repli','decalage_repli','angle_repli',
        'sens_rotation','imprimer_symboles',
        )
    actions = [views.svg]
    
admin.site.register(Plan, PlanAdmin)
