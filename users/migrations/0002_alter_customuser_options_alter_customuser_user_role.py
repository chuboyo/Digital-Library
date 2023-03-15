# Generated by Django 4.1.3 on 2023-01-21 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['first_name']},
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_role',
            field=models.CharField(choices=[('manager', 'Manager'), ('content_manager', 'Content Manager'), ('contributor', 'Contributor'), ('commenter', 'Commenter'), ('viewer', 'Viewer')], default='viewer', max_length=20),
        ),
    ]
