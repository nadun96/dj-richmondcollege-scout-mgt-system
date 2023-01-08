# Generated by Django 4.0 on 2023-01-02 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_memberrole_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complete',
            name='completed',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='memberrole',
            name='role',
            field=models.IntegerField(blank=True, choices=[(4, 'Storekeeper'), (1, 'Admin'), (2, 'Member'), (3, 'Secretary')]),
        ),
    ]