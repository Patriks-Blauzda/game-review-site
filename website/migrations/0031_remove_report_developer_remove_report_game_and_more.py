# Generated by Django 4.1.5 on 2023-06-05 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0030_report_developer_report_game_report_post_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='developer',
        ),
        migrations.RemoveField(
            model_name='report',
            name='game',
        ),
        migrations.RemoveField(
            model_name='report',
            name='post',
        ),
        migrations.RemoveField(
            model_name='report',
            name='publisher',
        ),
        migrations.AddField(
            model_name='report',
            name='count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
