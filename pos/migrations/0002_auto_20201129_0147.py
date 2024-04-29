# Generated by Django 3.0.6 on 2020-11-29 01:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('prenoms', models.CharField(max_length=200)),
                ('numero_cnib', models.CharField(max_length=200)),
                ('solde', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Depot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.IntegerField(default=0)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.Client')),
            ],
        ),
        migrations.AddField(
            model_name='vente',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pos.Client'),
        ),
    ]
