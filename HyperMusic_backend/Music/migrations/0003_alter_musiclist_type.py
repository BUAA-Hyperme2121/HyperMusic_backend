# Generated by Django 3.2.18 on 2023-05-21 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Music', '0002_auto_20230521_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musiclist',
            name='type',
            field=models.IntegerField(default=1),
        ),
    ]
