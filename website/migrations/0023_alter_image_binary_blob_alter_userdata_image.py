# Generated by Django 4.1.5 on 2023-03-22 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0022_userdata_user_alter_userdata_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='binary_blob',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='image',
            field=models.TextField(blank=True, null=True),
        ),
    ]
