from django.db import migrations

TESTIMONIALS = [
    {
        'name': 'Adaeze O.', 'city': 'Lagos', 'rating': 5, 'tone': 'cream',
        'product_name': 'Robe Adire Indigo',
        'text': "La robe portefeuille est arrivée dans un magnifique pochon en lin. Le tissu est encore plus beau qu'en photo, et la coupe est parfaitement flatteuse. Je la recommande sans hésiter.",
    },
    {
        'name': 'Kwame B.', 'city': 'Accra', 'rating': 5, 'tone': 'bone',
        'product_name': 'Montre Craft 42mm',
        'text': "La montre est arrivée rapidement et le bracelet est exactement dans la teinte marron que je voulais. Élégance discrète, finitions impeccables. Je reviens commander.",
    },
    {
        'name': 'Lerato M.', 'city': 'Nairobi', 'rating': 5, 'tone': 'sand',
        'product_name': 'Kaftan Sade Atelier',
        'text': "J'ai commandé trois pièces chez Sade Atelier. Les coupes sont très flatteuses et les matières respirantes. La livraison à Nairobi a pris 4 jours, bien emballé.",
    },
    {
        'name': 'Fatou D.', 'city': 'Dakar', 'rating': 5, 'tone': 'rust',
        'product_name': 'Collier Brass Lagos',
        'text': "Le collier est superbe, la qualité du laiton est au rendez-vous. J'ai reçu tellement de compliments ! Le service client a aussi été très réactif pour mon suivi de commande.",
    },
    {
        'name': 'Amara T.', 'city': 'Abidjan', 'rating': 5, 'tone': 'indigo',
        'product_name': 'Ensemble Ankara Homme',
        'text': "Mon mari porte cet ensemble pour les fêtes et il est magnifique. La broderie est fine et les couleurs très vives. Taille conforme au guide. Merci Dino Market !",
    },
    {
        'name': 'Nkechi A.', 'city': 'Port Harcourt', 'rating': 4, 'tone': 'ochre',
        'product_name': 'Sac Cuir Artisan',
        'text': "Le sac est solide et élégant, le cuir sent bon et les coutures sont bien faites. Légèrement plus petit que ce que j'imaginais mais la qualité vaut chaque centime.",
    },
]


def seed(apps, schema_editor):
    Testimonial = apps.get_model('products', 'Testimonial')
    for data in TESTIMONIALS:
        Testimonial.objects.get_or_create(name=data['name'], city=data['city'], defaults=data)


def unseed(apps, schema_editor):
    Testimonial = apps.get_model('products', 'Testimonial')
    Testimonial.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_testimonial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
