# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-11 20:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exploration', '0013_auto_20181111_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='shardhavenobstacle',
            name='haven_types',
            field=models.ManyToManyField(blank=True, related_name='_shardhavenobstacle_haven_types_+', to='exploration.ShardhavenType'),
        ),
    ]
