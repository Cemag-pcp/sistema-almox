# Generated by Django 5.0.6 on 2024-10-18 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacao', '0010_solicitacaocadastroitem_cc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaocadastroitem',
            name='quantidade',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]