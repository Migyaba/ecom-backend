from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_seed_category_covers'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('product_name', models.CharField(blank=True, help_text='Nom du produit acheté', max_length=200)),
                ('rating', models.PositiveSmallIntegerField(default=5)),
                ('tone', models.CharField(
                    choices=[('cream','Cream'),('bone','Bone'),('sand','Sand'),('indigo','Indigo'),('rust','Rust'),('ochre','Ochre')],
                    default='cream', max_length=20,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
