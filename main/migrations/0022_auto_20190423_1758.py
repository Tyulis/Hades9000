# Generated by Django 2.2 on 2019-04-23 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20190423_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpgroup',
            name='rs10role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs1role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs2role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs3role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs4role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs5role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs6role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs7role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs8role',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpgroup',
            name='rs9role',
            field=models.IntegerField(null=True),
        ),
    ]