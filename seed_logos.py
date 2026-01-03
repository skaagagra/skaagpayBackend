import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skaagpay_backend.settings')
django.setup()

from recharge.models import Operator

operators = [
    {'name': 'Airtel', 'category': 'MOBILE_PREPAID', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Airtel_logo.svg/200px-Airtel_logo.svg.png'},
    {'name': 'Jio', 'category': 'MOBILE_PREPAID', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Reliance_Jio_Logo.svg/200px-Reliance_Jio_Logo.svg.png'},
    {'name': 'Vi', 'category': 'MOBILE_PREPAID', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Vodafone_Idea_logo.svg/200px-Vodafone_Idea_logo.svg.png'},
    {'name': 'BSNL', 'category': 'MOBILE_PREPAID', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Bharat_Sanchar_Nigam_Limited_logo.svg/200px-Bharat_Sanchar_Nigam_Limited_logo.svg.png'},
    {'name': 'Dish TV', 'category': 'DTH', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Dish_TV_logo.svg/200px-Dish_TV_logo.svg.png'},
    {'name': 'Tata Play', 'category': 'DTH', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tata_Play_Logo.svg/200px-Tata_Play_Logo.svg.png'},
]

for op_data in operators:
    op, created = Operator.objects.get_or_create(name=op_data['name'], category=op_data['category'])
    op.logo_url = op_data['logo_url']
    op.save()
    print(f"{'Created' if created else 'Updated'} {op.name}")
