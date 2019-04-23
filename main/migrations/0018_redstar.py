# Generated by Django 2.1.1 on 2019-03-29 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20190324_1840'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedStar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(default=1)),
                ('launch', models.DateTimeField(null=True)),
                ('corp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Corporation')),
                ('player1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player1', to='main.Player')),
                ('player2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player2', to='main.Player')),
                ('player3', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player3', to='main.Player')),
                ('player4', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player4', to='main.Player')),
            ],
        ),
    ]