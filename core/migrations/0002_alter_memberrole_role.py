# Generated by Django 4.0 on 2022-12-31 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberrole',
            name='role',
            field=models.IntegerField(blank=True, choices=[(3, 'Secretary'), (1, 'Admin'), (4, 'Storekeeper'), (2, 'Member')]),
        ),
    ]