# Generated by Django 4.1.5 on 2023-05-31 14:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0027_comment_date_comment_profileuserdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=120)),
                ('developer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.developer')),
                ('game', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.game')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.post')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.publisher')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
