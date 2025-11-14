from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='rating',
            field=models.DecimalField(
                max_digits=4,
                decimal_places=2,
                default=0.00,
                verbose_name="Рейтинг",
                help_text="Значение от 0.00 до 10.00"
            ),
        ),
    ]