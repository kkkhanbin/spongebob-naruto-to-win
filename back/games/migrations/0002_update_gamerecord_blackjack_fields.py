from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamerecord',
            name='game',
            field=models.CharField(
                choices=[
                    ('roulette', 'Roulette'),
                    ('lotto', 'Lotto'),
                    ('blackjack', 'Blackjack'),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='gamerecord',
            name='result',
            field=models.CharField(max_length=100),
        ),
    ]
