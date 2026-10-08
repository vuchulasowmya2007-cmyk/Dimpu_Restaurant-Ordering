from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from restaurant.models import Category, MenuItem, Order, OrderItem


class RestaurantModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Appetizers",
            slug="appetizers",
            icon="bi-egg-fried"
        )
        self.item = MenuItem.objects.create(
            category=self.category,
            name="Truffle Fries",
            price=Decimal("10.00"),
            is_vegetarian=True,
            is_available=True
        )

    def test_menu_item_str_and_properties(self):
        self.assertEqual(str(self.category), "Appetizers")
        self.assertEqual(str(self.item), "Truffle Fries ($10.00)")
        self.assertTrue(self.item.is_vegetarian)

    def test_order_and_items_creation(self):
        order = Order.objects.create(
            customer_name="John Doe",
            customer_phone="1234567890",
            table_number="Table 1",
            subtotal=Decimal("20.00"),
            tax_amount=Decimal("1.00"),
            total_amount=Decimal("21.00"),
            status=Order.STATUS_RECEIVED
        )
        self.assertTrue(order.order_number.startswith("ORD-"))
        self.assertEqual(order.progress_percentage, 25)

        order_item = OrderItem.objects.create(
            order=order,
            menu_item=self.item,
            quantity=2,
            price=self.item.price
        )
        self.assertEqual(order_item.item_subtotal, Decimal("20.00"))
        self.assertEqual(order.item_count, 2)


class RestaurantViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="Main Course",
            slug="main-course",
            icon="bi-fire"
        )
        self.item = MenuItem.objects.create(
            category=self.category,
            name="Classic Burger",
            description="Juicy burger with cheddar",
            price=Decimal("12.00"),
            is_vegetarian=False,
            is_available=True
        )

    def test_menu_view_status_code(self):
        response = self.client.get(reverse('restaurant:menu'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Classic Burger")
        self.assertContains(response, "$12.00")

    def test_add_to_cart_and_session(self):
        response = self.client.post(
            reverse('restaurant:add_to_cart'),
            data={'item_id': self.item.id, 'quantity': 2}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['item_count'], 2)
        self.assertEqual(data['subtotal'], "24.00")
        self.assertEqual(data['tax_amount'], "1.20")
        self.assertEqual(data['total_amount'], "25.20")

    def test_checkout_workflow(self):
        # 1. Add item to cart
        self.client.post(
            reverse('restaurant:add_to_cart'),
            data={'item_id': self.item.id, 'quantity': 1}
        )

        # 2. Post checkout form
        response = self.client.post(reverse('restaurant:checkout'), {
            'table_number': 'Table 1',
            'customer_name': 'Jane Smith',
            'customer_phone': '555-0123',
            'customer_email': 'jane@example.com',
            'special_instructions': 'No onions please',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Order should be created in DB
        order = Order.objects.filter(customer_name='Jane Smith').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.table_number, 'Table 1')
        self.assertEqual(order.subtotal, Decimal('12.00'))
        self.assertEqual(order.tax_amount, Decimal('0.60'))
        self.assertEqual(order.total_amount, Decimal('12.60'))
        self.assertEqual(order.status, Order.STATUS_RECEIVED)

        # Session cart should now be empty
        session = self.client.session
        self.assertEqual(session.get('cart'), {})

    def test_order_status_api_and_tracking(self):
        order = Order.objects.create(
            customer_name="Bob",
            table_number="Table 3",
            subtotal=Decimal('10.00'),
            tax_amount=Decimal('0.50'),
            total_amount=Decimal('10.50'),
            status=Order.STATUS_RECEIVED
        )
        response = self.client.get(reverse('restaurant:order_status_api', args=[order.order_number]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], Order.STATUS_RECEIVED)

    def test_kitchen_dashboard_and_status_update(self):
        order = Order.objects.create(
            customer_name="Alice",
            table_number="Table 4",
            subtotal=Decimal('15.00'),
            tax_amount=Decimal('0.75'),
            total_amount=Decimal('15.75'),
            status=Order.STATUS_RECEIVED
        )

        # Advance order to PREPARING
        response = self.client.post(
            reverse('restaurant:update_order_status', args=[order.order_number]),
            {'status': Order.STATUS_PREPARING},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PREPARING)
