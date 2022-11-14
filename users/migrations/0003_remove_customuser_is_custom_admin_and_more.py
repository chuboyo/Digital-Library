# Generated by Django 4.1.3 on 2022-11-05 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_customuser_is_regular_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_custom_admin',
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_role',
            field=models.CharField(choices=[('is_custom_admin', 'Admin'), ('is_manager', 'Manager'), ('is_content_manager', 'Content_Manager'), ('is_contributor', 'Contributor'), ('is_commenter', 'Commenter'), ('is_viewer', 'Viewer')], default='is_viewer', max_length=20),
        ),
    ]
