# Generated by Django 2.1.1 on 2019-02-16 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerupdate',
            name='groupadmin',
            field=models.BooleanField(default=False),
        ),
    ]
