# Generated by Django 4.1.5 on 2023-03-13 13:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0017_likesusermap'),
    ]

    operations = [
        migrations.AddField(
            model_name='likesusermap',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.post'),
        ),
    ]
