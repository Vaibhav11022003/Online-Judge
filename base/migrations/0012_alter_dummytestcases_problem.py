# Generated by Django 5.0.6 on 2024-07-06 18:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_problem_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dummytestcases',
            name='problem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.problem'),
        ),
    ]
