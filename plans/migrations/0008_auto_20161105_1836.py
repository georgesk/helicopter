# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-05 18:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plans', '0007_auto_20161105_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name="Date de création de l'expérience")),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='plan',
            name='auteur',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='variationaa',
            name='creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date de création de la variation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='experience',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plans.Plan'),
        ),
        migrations.AddField(
            model_name='experience',
            name='var1',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, to='plans.variationAA'),
        ),
    ]
