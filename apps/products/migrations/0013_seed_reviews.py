from django.db import migrations

# (product_slug, user_id, rating, body)
REVIEWS = [
    # Robe Portefeuille Ankara
    ('robe-portefeuille-ankara', 1, 5, "Tissu magnifique, coupe parfaite. Je l'ai portée à un mariage et j'ai reçu tellement de compliments. La livraison a été rapide et l'emballage soigné."),
    ('robe-portefeuille-ankara', 3, 5, "Exactement comme sur les photos. La robe est confortable même par forte chaleur. Je recommande vivement cette boutique."),
    ('robe-portefeuille-ankara', 5, 4, "Très belle robe. La taille est conforme au guide. Légèrement plus longue que prévu mais ça va bien avec des sandales."),

    # Ensemble Bogolan Femme
    ('ensemble-bogolan-femme', 2, 5, "Les motifs bogolan sont authentiques et les couleurs ne se sont pas délavées après plusieurs lavages. Superbe pièce artisanale."),
    ('ensemble-bogolan-femme', 4, 4, "Beau travail artisanal. Le tissu est un peu épais pour les journées très chaudes mais parfait le soir. Je suis satisfaite."),

    # Boubou Brodé Ivoire
    ('boubou-brode-ivoire', 6, 5, "La broderie est d'une finesse exceptionnelle. Porté pour une cérémonie, il était impeccable. Livraison en 3 jours à Abidjan."),
    ('boubou-brode-ivoire', 7, 5, "Qualité premium, taille XL parfaite. Mon mari l'a porté pour une fête et il était le plus élégant de l'assemblée !"),

    # Agbada Contemporain
    ('agbada-contemporain', 1, 5, "Coupe moderne qui modernise le style traditionnel. Les broderies sont précises et le tissu tient bien. Très satisfait."),
    ('agbada-contemporain', 5, 4, "Très bel ensemble. La veste est légèrement ample mais le pantalon taille juste. N'hésitez pas à prendre votre taille habituelle."),

    # Chemise Kente Slim
    ('chemise-kente-slim', 2, 5, "Les couleurs du kente sont vibrantes et authentiques. Coupe slim parfaite pour moi. Idéale pour le bureau ou une soirée."),
    ('chemise-kente-slim', 6, 5, "Superbe chemise ! J'en ai commandé deux. La qualité du tissu est excellente et les finitions sont soignées."),
    ('chemise-kente-slim', 4, 4, "Belle chemise, couleurs fidèles à la photo. Légèrement sèche au premier lavage mais se détend bien après."),

    # Collier Perles Or Akan
    ('collier-perles-or-akan', 3, 5, "Les perles sont dorées et brillantes. Le fermoir est solide. Je le porte tous les jours depuis deux semaines et aucune oxydation."),
    ('collier-perles-or-akan', 7, 5, "Magnifique bijou ! La longueur est parfaite. Livré dans un beau coffret, idéal pour offrir en cadeau."),
    ('collier-perles-or-akan', 1, 5, "Très beau collier, il correspond parfaitement aux photos. La qualité des perles est au rendez-vous. Je recommande."),

    # Boucles Masai Laiton
    ('boucles-masai-laiton', 5, 5, "Boucles légères et très bien finies. Le laiton est de qualité. Je les porte depuis des semaines sans aucune réaction cutanée."),
    ('boucles-masai-laiton', 3, 4, "Très jolies boucles d'oreilles. Un peu grandes pour moi mais très bien pour une soirée. Belle pièce artisanale."),

    # Panier Osier Tressé
    ('panier-osier-tresse', 6, 5, "Panier solide et très esthétique. Le tressage est impeccable. Je l'utilise comme sac de plage et tout le monde me demande où je l'ai trouvé !"),
    ('panier-osier-tresse', 2, 4, "Beau panier artisanal. Les finitions sont soignées. Légèrement plus petit que sur la photo mais parfait pour les emplettes."),

    # Coussin Batik Mali
    ('coussin-batik-mali', 4, 5, "Coussin magnifique ! Les motifs batik sont authentiques et la housse est de bonne qualité. Il apporte une touche d'Afrique à mon salon."),
    ('coussin-batik-mali', 7, 5, "J'en ai commandé deux pour mon canapé. Les couleurs sont exactement comme sur les photos. Très satisfaite !"),
    ('coussin-batik-mali', 1, 4, "Beau coussin. La fermeture éclair est solide. Le tissu est légèrement rêche au toucher mais c'est normal pour du batik authentique."),

    # Montre Acier Doré
    ('montre-acier-dore', 3, 5, "Montre élégante au quotidien. Le bracelet en acier est confortable et le cadran bien lisible. Rapport qualité/prix excellent."),
    ('montre-acier-dore', 5, 5, "Design épuré et moderne. La montre est lourde ce qui lui donne un aspect premium. Livraison soignée avec coffret."),
    ('montre-acier-dore', 2, 4, "Très belle montre. Le mécanisme est précis après 2 semaines d'utilisation. Je retire une étoile car le verre est sensible aux rayures."),
]


def seed(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    User = apps.get_model('users', 'User')
    Review = apps.get_model('products', 'Review')

    for slug, user_id, rating, body in REVIEWS:
        try:
            product = Product.objects.get(slug=slug)
            user = User.objects.get(pk=user_id)
            Review.objects.get_or_create(
                product=product,
                user=user,
                defaults={'rating': rating, 'body': body},
            )
        except (Product.DoesNotExist, User.DoesNotExist):
            pass


def unseed(apps, schema_editor):
    Review = apps.get_model('products', 'Review')
    Review.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_seed_testimonials'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
