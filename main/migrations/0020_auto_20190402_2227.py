# Generated by Django 2.1.1 on 2019-04-02 22:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_corpgroup_custom_commands'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='redstar',
            name='corp',
        ),
        migrations.RemoveField(
            model_name='redstar',
            name='launch',
        ),
        migrations.AddField(
            model_name='player',
            name='rsready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='redstar',
            name='group',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='main.CorpGroup'),
            preserve_default=False,
        ),
    ]
