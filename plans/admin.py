from django.contrib import admin
from plans.models import Plan

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
    fields = ('hauteur_helice',)

admin.site.register(Plan, PlanAdmin)
