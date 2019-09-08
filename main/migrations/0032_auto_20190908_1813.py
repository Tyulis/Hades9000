# Generated by Django 2.2 on 2019-09-08 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_corpgroup_afkchannels'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='redstar',
            name='group',
        ),
        migrations.AddField(
            model_name='redstar',
            name='channels',
            field=models.TextField(default='[-1, -1, -1, -1]'),
        ),
        migrations.AddField(
            model_name='redstar',
            name='corp',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='main.Corporation'),
            preserve_default=False,
        ),
    ]
