from django.contrib import admin
from .models import Plan, Profil, variationAA, Experience
import plans.views as views
from .forms import variationAAAdminForm
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
        ('auteur'),
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

class variationAAAdmin(admin.ModelAdmin):
    class Media:
        js = (
            '/static/plans/js/jquery/jquery.js',
            '/static/plans/js/jquery-ui/jquery-ui.js',
            '/static/plans/js/select2.js/select2.js',
            '/static/plans/js/expAA.js',
        )
        css = {
            'all': (
                '/static/plans/css/base.css',
                '/static/plans/js/jquery-ui/css/smoothness/jquery-ui.min.css',
                '/static/plans/js/select2.js/select2.css',
            ),
        }
    list_display  = ["auteur", "param1", "val11", "val12", "val13", "param2", "val21", "val22", "val23", "val24"]
    form = variationAAAdminForm
    
admin.site.register(variationAA, variationAAAdmin)

class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["auteur", "creation", "plan", "var1"]


admin.site.register(Experience, ExperienceAdmin)
