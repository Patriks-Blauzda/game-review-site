# Generated by Django 4.1.5 on 2023-02-14 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_alter_image_binary_blob'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='filename',
        ),
        migrations.AlterField(
            model_name='image',
            name='binary_blob',
            field=models.TextField(),
        ),
    ]
