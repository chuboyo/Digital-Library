# Generated by Django 4.1.3 on 2022-11-14 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_emailrequest'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmailRequest',
        ),
    ]
