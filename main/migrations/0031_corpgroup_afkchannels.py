# Generated by Django 2.2 on 2019-09-07 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20190907_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpgroup',
            name='afkchannels',
            field=models.TextField(default='[]'),
        ),
    ]
