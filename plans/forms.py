from django import forms
from django.contrib import admin
from .models import variationAA, variationBA
from django.utils.safestring import mark_safe


class variationAAAdminForm(forms.ModelForm):
    val11=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val12=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val13=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val21=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val22=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val23=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val24=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val1=forms.CharField(widget=forms.SelectMultiple())
    val2=forms.CharField(widget=forms.SelectMultiple())
    class Meta:
        model = variationAA
        fields = ("auteur","param1", "val11", "val12", "val13", "param2", "val21", "val22", "val23", "val24")

    def clean(self):
        errors = {}
        cleaned_data = super(variationAAAdminForm, self).clean()
        v1 = eval(cleaned_data.get("val1"))
        v2 = eval(cleaned_data.get("val2"))
        p1 = cleaned_data.get("param1")
        p2 = cleaned_data.get("param2")
        if p1==p2:
            errors.setdefault('param1',[]).append("Les paramètres 1 et 2 doivent être deux grandeurs différentes !")
        if len(v1) != 3:
            errors.setdefault('val1',[]).append("Le premier paramètre doit avoir trois valeurs différentes")
        else:
            cleaned_data["val11"]=int(v1[0])
            cleaned_data["val12"]=int(v1[1])
            cleaned_data["val13"]=int(v1[2])
        if len(v2) != 4:
            errors.setdefault('val2',[]).append("Le premier paramètre doit avoir quatre valeurs différentes")
        else:
            cleaned_data["val21"]=int(v2[0])
            cleaned_data["val22"]=int(v2[1])
            cleaned_data["val23"]=int(v2[2])
            cleaned_data["val24"]=int(v2[3])
        if len( errors ) > 0: 
            raise forms.ValidationError(errors)

class HorizontalRadioRenderer(forms.RadioSelect.renderer):
  def render(self):
    return mark_safe('\n'.join(['%s\n' % w for w in self]))

class variationBAAdminForm(forms.ModelForm):
    val31=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val32=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val33=forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    val=forms.CharField(widget=forms.SelectMultiple())
    class Meta:
        model = variationBA
        fields = ("auteur","param1", "param2", "param3", "val31", "val32", "val33")

    def clean(self):
        errors = {}
        cleaned_data = super(variationBAAdminForm, self).clean()
        v = eval(cleaned_data.get("val"))
        p1 = cleaned_data.get("param1")
        p2 = cleaned_data.get("param2")
        if p1==p2:
            errors.setdefault('param1',[]).append("Les paramètres 1 et 2 doivent être deux grandeurs différentes !")
        if len(v) != 3:
            errors.setdefault('val1',[]).append("Le dernier paramètre doit avoir trois valeurs différentes")
        else:
            cleaned_data["val31"]=int(v[0])
            cleaned_data["val32"]=int(v[1])
            cleaned_data["val33"]=int(v[2])
        if len( errors ) > 0: 
            raise forms.ValidationError(errors)
