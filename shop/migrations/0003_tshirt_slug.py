# Generated by Django 3.1.2 on 2020-10-28 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_remove_tshirt_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='tshirt',
            name='slug',
            field=models.CharField(default='', max_length=200, null=True),
        ),
    ]
