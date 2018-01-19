# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import api.models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    atomic = False

    operations = [
        migrations.CreateModel(
            name='ActivityTrackFile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to=api.models.track_upload_path)),
            ],
        ),
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['-datetime']},
        ),
        migrations.AlterModelOptions(
            name='activitytrack',
            options={'ordering': ['trim_start']},
        ),
        migrations.AlterModelTable(
            name='activity',
            table=None,
        ),
        migrations.AlterModelTable(
            name='activitytrack',
            table=None,
        ),
        migrations.AlterModelTable(
            name='activitytrackpoint',
            table=None,
        ),
        migrations.AddField(
            model_name='activitytrackfile',
            name='track',
            field=models.ForeignKey(related_name='file', to='api.ActivityTrack', on_delete=models.CASCADE),
        ),
    ]
