# Generated by Django 2.2 on 2019-08-31 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_remove_question_topics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corpgroup',
            name='faqcolor',
            field=models.IntegerField(default=0),
        ),
    ]
