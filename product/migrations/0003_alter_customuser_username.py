# Generated by Django 5.1.7 on 2025-03-27 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=50),
        ),
    ]
