from django.db import migrations

COVERS = {
    'women':   'https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=800&q=75',
    'men':     'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?auto=format&fit=crop&w=800&q=75',
    'jewelry': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=800&q=75',
    'home':    'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=75',
    'watches': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=75',
    'bags':    'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=75',
    'shoes':   'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=75',
}


def seed(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    for slug, url in COVERS.items():
        Category.objects.filter(slug=slug).update(cover_url=url)


def unseed(apps, schema_editor):
    from django.db.models import Q
    Category = apps.get_model('products', 'Category')
    Category.objects.filter(slug__in=COVERS.keys()).update(cover_url='')


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_category_cover_url'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
