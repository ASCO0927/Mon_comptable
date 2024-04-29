# Generated by Django 3.0.6 on 2020-11-29 22:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0003_auto_20201129_2159'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoriqueClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.IntegerField(default=0)),
                ('type_transaction', models.CharField(max_length=200)),
                ('solde_avant', models.IntegerField(default=0)),
                ('solde_apres', models.IntegerField(default=0)),
                ('date_transaction', models.DateTimeField(verbose_name='date transaction')),
            ],
        ),
        migrations.RenameModel(
            old_name='Depot',
            new_name='Avance',
        ),
        migrations.DeleteModel(
            name='TransactionsClient',
        ),
        migrations.AddField(
            model_name='historiqueclient',
            name='avance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pos.Avance'),
        ),
        migrations.AddField(
            model_name='historiqueclient',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.Client'),
        ),
        migrations.AddField(
            model_name='historiqueclient',
            name='vente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pos.Vente'),
        ),
    ]
