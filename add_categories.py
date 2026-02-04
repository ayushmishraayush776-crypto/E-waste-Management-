#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ewaste_project.settings')
django.setup()

from ewaste.models import EWasteCategory

# Create categories
categories_data = [
    {"name": "Smartphones", "description": "Mobile phones and smartphones", "icon": "📱"},
    {"name": "Laptops & Computers", "description": "Laptops, desktops, and computer equipment", "icon": "💻"},
    {"name": "Tablets & E-Readers", "description": "Tablets, iPads, and e-readers", "icon": "📱"},
    {"name": "Televisions", "description": "TVs and display screens", "icon": "📺"},
    {"name": "Audio Equipment", "description": "Speakers, headphones, and audio devices", "icon": "🔊"},
    {"name": "Printers & Scanners", "description": "Printers, copiers, and scanners", "icon": "🖨️"},
    {"name": "Gaming Devices", "description": "Gaming consoles and accessories", "icon": "🎮"},
    {"name": "Cameras & Photography", "description": "Digital cameras and photography equipment", "icon": "📷"},
    {"name": "Home Appliances", "description": "Microwaves, washing machines, and other appliances", "icon": "🏠"},
    {"name": "Cables & Accessories", "description": "Chargers, cables, and other accessories", "icon": "🔌"},
]

for category in categories_data:
    obj, created = EWasteCategory.objects.get_or_create(
        name=category["name"],
        defaults={
            "description": category["description"],
            "icon": category["icon"]
        }
    )
    if created:
        print(f"✓ Created category: {category['name']}")
    else:
        print(f"• Category already exists: {category['name']}")

print("\n=== All Categories ===")
for cat in EWasteCategory.objects.all():
    print(f"- {cat.name}")
