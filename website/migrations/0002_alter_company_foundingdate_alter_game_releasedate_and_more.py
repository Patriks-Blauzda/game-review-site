# Generated by Django 4.1.5 on 2023-01-24 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='foundingdate',
            field=models.DateField(verbose_name='date founded'),
        ),
        migrations.AlterField(
            model_name='game',
            name='releasedate',
            field=models.DateField(verbose_name='date released'),
        ),
        migrations.AlterField(
            model_name='studio',
            name='foundingdate',
            field=models.DateField(verbose_name='date founded'),
        ),
    ]
