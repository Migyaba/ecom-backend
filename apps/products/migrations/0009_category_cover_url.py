from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_sale_ends_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='cover_url',
            field=models.URLField(blank=True, help_text='Image de couverture par défaut (URL externe, Unsplash…)'),
        ),
    ]
