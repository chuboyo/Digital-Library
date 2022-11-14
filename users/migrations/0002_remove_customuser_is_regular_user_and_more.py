# Generated by Django 4.1.3 on 2022-11-05 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_regular_user',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_commenter',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_content_manager',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_contributor',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_manager',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_viewer',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
