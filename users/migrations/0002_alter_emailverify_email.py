# Generated by Django 4.2.1 on 2023-09-02 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverify',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
