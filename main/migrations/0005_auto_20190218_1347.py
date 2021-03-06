# Generated by Django 2.1.1 on 2019-02-18 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20190218_1322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerupdate',
            name='admin',
        ),
        migrations.RemoveField(
            model_name='playerupdate',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='playerupdate',
            name='groupadmin',
        ),
        migrations.RemoveField(
            model_name='playerupdate',
            name='groupcreator',
        ),
        migrations.AddField(
            model_name='player',
            name='admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='player',
            name='creator',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='player',
            name='groupadmin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='player',
            name='groupcreator',
            field=models.BooleanField(default=False),
        ),
    ]
