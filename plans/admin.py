from django.contrib import admin
from plans.models import Plan, Profil
import plans.views as views
from django.contrib.auth.models import User
from django.db.models.signals import post_save

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

### CRÉATION AUTOMATIQUE D'UN PROFIL À CHAQUE CRÉATION D'UTILISATEUR
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = Profil.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User)

class ProfilAdmin (admin.ModelAdmin):
    list_display  = ["user", "statut"]
    list_filter   = ["statut"]

admin.site.register(Profil, ProfilAdmin)
