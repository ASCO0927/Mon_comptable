# Generated by Django 3.0.6 on 2020-12-30 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0008_auto_20201230_1555'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='article',
            name='unicite_du_code_barres',
        ),
        migrations.AlterField(
            model_name='article',
            name='code_barres',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
    ]