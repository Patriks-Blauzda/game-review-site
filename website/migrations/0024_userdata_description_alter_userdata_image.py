# Generated by Django 4.1.5 on 2023-03-22 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0023_alter_image_binary_blob_alter_userdata_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.image'),
        ),
    ]
