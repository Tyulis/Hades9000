# Generated by Django 2.2 on 2019-09-07 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_corpgroup_faqcolor'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='afkduration',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='player',
            name='afkstart',
            field=models.IntegerField(default=-1),
        ),
    ]