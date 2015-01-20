# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activities', '0017_activiites_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(default=-1, related_name='activity', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
