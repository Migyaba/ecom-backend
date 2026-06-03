from django.db import migrations

CATEGORIES = [
    {'name': 'Mode Femme',    'slug': 'women',   'eyebrow': 'Pour Elle', 'tone': 'indigo'},
    {'name': 'Mode Homme',    'slug': 'men',     'eyebrow': 'Pour Lui',  'tone': 'bone'},
    {'name': 'Bijouterie',    'slug': 'jewelry', 'eyebrow': 'Bijoux',    'tone': 'brass'},
    {'name': 'Maison & Déco', 'slug': 'home',    'eyebrow': 'Décorer',   'tone': 'sand'},
    {'name': 'Horlogerie',    'slug': 'watches', 'eyebrow': 'Montres',   'tone': 'ink'},
]


def seed(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    for data in CATEGORIES:
        Category.objects.get_or_create(slug=data['slug'], defaults=data)


def unseed(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Category.objects.filter(slug__in=[c['slug'] for c in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_category_tone_eyebrow'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
