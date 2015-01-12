# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0012_rename_activity_to_activitytrack'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='activitytrackpoint',
            old_name='file_id',
            new_name='track_id',
        ),
        migrations.RemoveField(
            model_name='activitydetail',
            name='file_id',
        ),
        migrations.RemoveField(
            model_name='activitystat',
            name='file_id',
        ),
        migrations.AddField(
            model_name='activitydetail',
            name='activity_id',
            field=models.OneToOneField(related_name='details', default=1, to='activities.Activity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activitystat',
            name='activity_id',
            field=models.OneToOneField(related_name='stats', default=1, to='activities.Activity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activitytrack',
            name='activity_id',
            field=models.OneToOneField(related_name='track', default=1, to='activities.Activity'),
            preserve_default=False,
        ),
    ]
