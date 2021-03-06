# Generated by Django 2.2 on 2019-05-11 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20190423_1758'),
    ]

    operations = [
        migrations.RenameField(
            model_name='corporation',
            old_name='leadrole',
            new_name='lead1role',
        ),
        migrations.RenameField(
            model_name='corporation',
            old_name='wsrole',
            new_name='ws1role',
        ),
        migrations.AddField(
            model_name='corporation',
            name='lead2role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corporation',
            name='ws2role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='ws',
            name='slot',
            field=models.IntegerField(default=1),
        ),
    ]
