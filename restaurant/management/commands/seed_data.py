from decimal import Decimal
from django.core.management.base import BaseCommand
from restaurant.models import Category, MenuItem, Order, OrderItem


class Command(BaseCommand):
    help = "Populate the database with sample categories, menu items, and demo orders."

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories and menu items...")

        # 1. Categories
        categories_data = [
            {"name": "Appetizers", "slug": "appetizers", "icon": "bi-egg-fried", "display_order": 1},
            {"name": "Main Course", "slug": "main-course", "icon": "bi-fire", "display_order": 2},
            {"name": "Desserts", "slug": "desserts", "icon": "bi-cake2", "display_order": 3},
            {"name": "Beverages", "slug": "beverages", "icon": "bi-cup-straw", "display_order": 4},
        ]

        cat_objs = {}
        for cat in categories_data:
            obj, created = Category.objects.get_or_create(
                name=cat["name"],
                defaults={
                    "slug": cat["slug"],
                    "icon": cat["icon"],
                    "display_order": cat["display_order"],
                }
            )
            cat_objs[cat["name"]] = obj

        # 2. Menu Items
        menu_items_data = [
            # Appetizers
            {
                "category": "Appetizers",
                "name": "Crispy Truffle Fries",
                "description": "Hand-cut Idaho potatoes tossed in white truffle oil, grated aged parmesan, and fresh rosemary with garlic aioli.",
                "price": Decimal("8.99"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1576107232684-1279f3908594?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Appetizers",
                "name": "Artisanal Bruschetta",
                "description": "Toasted sourdough slices topped with heirloom tomatoes, fresh buffalo mozzarella, fragrant basil, and balsamic glaze.",
                "price": Decimal("9.50"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Appetizers",
                "name": "Smoked Buffalo Wings",
                "description": "Crispy glazed chicken wings tossed in homemade tangy buffalo sauce, served with blue cheese dip and celery sticks.",
                "price": Decimal("12.99"),
                "is_vegetarian": False,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Appetizers",
                "name": "Golden Calamari Fritti",
                "description": "Lightly battered wild-caught calamari rings served with lemon herb aioli and warm marinara dipping sauce.",
                "price": Decimal("13.50"),
                "is_vegetarian": False,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=600&q=80",
            },

            # Main Course
            {
                "category": "Main Course",
                "name": "Gourmet Wagyu Burger",
                "description": "Prime grilled Wagyu beef patty, melted aged cheddar, caramelized red onion jam, arugula, and brioche bun with fries.",
                "price": Decimal("18.99"),
                "is_vegetarian": False,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Main Course",
                "name": "Wild Mushroom Risotto",
                "description": "Creamy Arborio rice slowly simmered with porcini and cremini mushrooms, truffle butter, white wine, and parmesan.",
                "price": Decimal("16.50"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Main Course",
                "name": "Pan-Seared Atlantic Salmon",
                "description": "Crispy-skin Atlantic salmon fillet over garlic-infused mashed potatoes, sauteed asparagus, and lemon-dill cream.",
                "price": Decimal("22.50"),
                "is_vegetarian": False,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Main Course",
                "name": "Wood-Fired Margherita Pizza",
                "description": "San Marzano tomato sauce, fresh Fior di Latte mozzarella, fragrant basil leaves, and extra virgin olive oil.",
                "price": Decimal("15.00"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Main Course",
                "name": "Fettuccine Alfredo with Chicken",
                "description": "Fresh house-made fettuccine ribbons in rich parmesan cream sauce with grilled herb chicken breast.",
                "price": Decimal("17.99"),
                "is_vegetarian": False,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?auto=format&fit=crop&w=600&q=80",
            },

            # Desserts
            {
                "category": "Desserts",
                "name": "Classic Italian Tiramisu",
                "description": "Espresso-soaked ladyfingers layered with whipped mascarpone cream and dusted with fine Dutch cocoa powder.",
                "price": Decimal("8.50"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Desserts",
                "name": "Molten Chocolate Lava Cake",
                "description": "Warm dark Belgian chocolate cake with a molten center, served with Madagascan vanilla bean gelato.",
                "price": Decimal("9.50"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Desserts",
                "name": "New York Berry Cheesecake",
                "description": "Velvety baked cream cheesecake with a buttery graham cracker crust and wild summer berry compote.",
                "price": Decimal("8.00"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=600&q=80",
            },

            # Beverages
            {
                "category": "Beverages",
                "name": "Signature Cold Brew Coffee",
                "description": "Single-origin Arabica beans steeped for 18 hours, served over crystal clear ice with sweet vanilla cold foam.",
                "price": Decimal("5.50"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Beverages",
                "name": "Fresh Mint Limeade",
                "description": "Freshly squeezed Tahitian limes, crushed garden mint, raw cane syrup, and sparkling mineral water.",
                "price": Decimal("4.99"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Beverages",
                "name": "Berry Hibiscus Iced Tea",
                "description": "Brewed ruby hibiscus flowers infused with dried blackberries, pomegranate, and sweet orange zest.",
                "price": Decimal("5.25"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=600&q=80",
            },
            {
                "category": "Beverages",
                "name": "Creamy Mango Lassi",
                "description": "Chilled blend of sweet Alphonso mango pulp, probiotic Greek yogurt, cardamom, and roasted pistachios.",
                "price": Decimal("6.00"),
                "is_vegetarian": True,
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1527661591475-527312dd65f5?auto=format&fit=crop&w=600&q=80",
            },
        ]

        item_map = {}
        for item_data in menu_items_data:
            cat = cat_objs[item_data["category"]]
            obj, _ = MenuItem.objects.update_or_create(
                name=item_data["name"],
                defaults={
                    "category": cat,
                    "description": item_data["description"],
                    "price": item_data["price"],
                    "is_vegetarian": item_data["is_vegetarian"],
                    "is_available": item_data["is_available"],
                    "image_url": item_data["image_url"],
                }
            )
            item_map[item_data["name"]] = obj

        # 3. Sample Orders across different statuses for Kitchen Dashboard & Tracking
        if not Order.objects.exists():
            self.stdout.write("Creating demonstration orders...")
            demo_orders = [
                {
                    "customer_name": "Sarah Miller",
                    "customer_phone": "+1 (555) 234-8761",
                    "table_number": "Table 4",
                    "status": Order.STATUS_RECEIVED,
                    "special_instructions": "Extra aioli for truffle fries please.",
                    "items": [
                        ("Crispy Truffle Fries", 2),
                        ("Gourmet Wagyu Burger", 1),
                        ("Fresh Mint Limeade", 2),
                    ]
                },
                {
                    "customer_name": "David Chen",
                    "customer_phone": "+1 (555) 789-0123",
                    "table_number": "Table 2",
                    "status": Order.STATUS_PREPARING,
                    "special_instructions": "Make the risotto extra hot.",
                    "items": [
                        ("Wild Mushroom Risotto", 1),
                        ("Artisanal Bruschetta", 1),
                        ("Berry Hibiscus Iced Tea", 1),
                    ]
                },
                {
                    "customer_name": "Elena Rostova",
                    "customer_phone": "+1 (555) 345-6789",
                    "table_number": "Table 5",
                    "status": Order.STATUS_READY,
                    "special_instructions": "Gluten-sensitive precautions.",
                    "items": [
                        ("Pan-Seared Atlantic Salmon", 2),
                        ("Signature Cold Brew Coffee", 2),
                        ("Molten Chocolate Lava Cake", 1),
                    ]
                },
                {
                    "customer_name": "Marcus Aurelius",
                    "customer_phone": "+1 (555) 901-2345",
                    "table_number": "Table 1",
                    "status": Order.STATUS_COMPLETED,
                    "special_instructions": "Table by window enjoyed dinner.",
                    "items": [
                        ("Wood-Fired Margherita Pizza", 1),
                        ("Classic Italian Tiramisu", 1),
                    ]
                },
            ]

            for ord_data in demo_orders:
                subtotal = Decimal("0.00")
                order_items_to_create = []

                for item_name, qty in ord_data["items"]:
                    m_item = item_map.get(item_name)
                    if m_item:
                        cost = m_item.price * Decimal(qty)
                        subtotal += cost
                        order_items_to_create.append((m_item, qty, m_item.price))

                tax = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
                total = subtotal + tax

                order = Order.objects.create(
                    customer_name=ord_data["customer_name"],
                    customer_phone=ord_data["customer_phone"],
                    table_number=ord_data["table_number"],
                    status=ord_data["status"],
                    special_instructions=ord_data["special_instructions"],
                    subtotal=subtotal,
                    tax_amount=tax,
                    total_amount=total,
                )

                for m_item, qty, price in order_items_to_create:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=m_item,
                        quantity=qty,
                        price=price
                    )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with categories, menu items, and demo orders."))
