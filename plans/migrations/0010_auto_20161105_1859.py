# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-05 18:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0009_variationaa_autuer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='variationaa',
            old_name='autuer',
            new_name='auteur',
        ),
    ]
