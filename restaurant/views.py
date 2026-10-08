import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Category, MenuItem, Order, OrderItem
from .forms import OrderCheckoutForm, OrderStatusUpdateForm


TAX_RATE = Decimal('0.05')  # 5% standard sales tax


def get_session_cart(request):
    """Retrieve or initialize the session-based cart dict: {str(item_id): int(quantity)}"""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']


def save_session_cart(request, cart):
    """Persist modified cart dict into Django session"""
    request.session['cart'] = cart
    request.session.modified = True


def calculate_cart_details(cart_dict):
    """
    Server-side price, subtotal, tax and total computation.
    Guarantees no client price tampering can succeed.
    """
    items = []
    subtotal = Decimal('0.00')

    if not cart_dict:
        return {
            'items': items,
            'subtotal': subtotal,
            'tax_amount': Decimal('0.00'),
            'total_amount': Decimal('0.00'),
            'item_count': 0,
        }

    item_ids = [int(k) for k in cart_dict.keys() if str(k).isdigit()]
    menu_items = {item.id: item for item in MenuItem.objects.filter(id__in=item_ids)}

    total_quantity = 0
    for item_id_str, qty in cart_dict.items():
        try:
            item_id = int(item_id_str)
            quantity = int(qty)
        except (ValueError, TypeError):
            continue

        if quantity <= 0:
            continue

        menu_item = menu_items.get(item_id)
        if not menu_item:
            continue

        item_subtotal = menu_item.price * Decimal(quantity)
        subtotal += item_subtotal
        total_quantity += quantity

        items.append({
            'menu_item': menu_item,
            'quantity': quantity,
            'price': menu_item.price,
            'subtotal': item_subtotal,
            'is_available': menu_item.is_available,
        })

    tax_amount = (subtotal * TAX_RATE).quantize(Decimal('0.01'))
    total_amount = subtotal + tax_amount

    return {
        'items': items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'item_count': total_quantity,
    }


@ensure_csrf_cookie
def menu_view(request):
    """
    Main restaurant menu page grouped by categories.
    Supports search query, category filtering, and vegetarian toggle.
    """
    categories = Category.objects.prefetch_related('menu_items').all()
    query = request.GET.get('q', '').strip()
    selected_category_slug = request.GET.get('category', '').strip()
    vegetarian_only = request.GET.get('veg', '') == '1'

    items_qs = MenuItem.objects.select_related('category').filter(is_available=True)

    if query:
        items_qs = items_qs.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if selected_category_slug and selected_category_slug != 'all':
        items_qs = items_qs.filter(category__slug=selected_category_slug)

    if vegetarian_only:
        items_qs = items_qs.filter(is_vegetarian=True)

    # Group items by category for structured display
    category_map = {}
    for cat in categories:
        cat_items = [item for item in items_qs if item.category_id == cat.id]
        if cat_items or not (query or selected_category_slug or vegetarian_only):
            category_map[cat] = cat_items

    cart_dict = get_session_cart(request)
    cart_summary = calculate_cart_details(cart_dict)

    context = {
        'categories': categories,
        'category_map': category_map,
        'all_items': items_qs,
        'search_query': query,
        'selected_category_slug': selected_category_slug or 'all',
        'vegetarian_only': vegetarian_only,
        'cart_summary': cart_summary,
    }
    return render(request, 'restaurant/menu.html', context)


def cart_view(request):
    """
    Cart review and preparation page.
    """
    cart_dict = get_session_cart(request)
    cart_summary = calculate_cart_details(cart_dict)
    form = OrderCheckoutForm()

    context = {
        'cart_summary': cart_summary,
        'form': form,
    }
    return render(request, 'restaurant/cart.html', context)


@require_POST
def add_to_cart(request):
    """
    API endpoint to add or increment item in session cart.
    Accepts JSON or form-encoded POST.
    """
    try:
        data = json.loads(request.body) if request.body and request.content_type == 'application/json' else request.POST
        item_id = str(data.get('item_id'))
        quantity = int(data.get('quantity', 1))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Invalid request parameters'}, status=400)

    if not item_id:
        return JsonResponse({'success': False, 'error': 'Menu item ID is required'}, status=400)

    menu_item = get_object_or_404(MenuItem, id=item_id)
    if not menu_item.is_available:
        return JsonResponse({'success': False, 'error': f"'{menu_item.name}' is currently out of stock."}, status=400)

    cart = get_session_cart(request)
    current_qty = cart.get(item_id, 0)
    new_qty = current_qty + quantity
    if new_qty > 20:
        new_qty = 20  # sane limit per order

    cart[item_id] = new_qty
    save_session_cart(request, cart)

    summary = calculate_cart_details(cart)
    return JsonResponse({
        'success': True,
        'message': f"Added '{menu_item.name}' to your order.",
        'item_id': item_id,
        'item_name': menu_item.name,
        'quantity': new_qty,
        'item_count': summary['item_count'],
        'subtotal': f"{summary['subtotal']:.2f}",
        'tax_amount': f"{summary['tax_amount']:.2f}",
        'total_amount': f"{summary['total_amount']:.2f}",
    })


@require_POST
def update_cart_quantity(request):
    """
    Update item quantity or remove item from session cart.
    """
    try:
        data = json.loads(request.body) if request.body and request.content_type == 'application/json' else request.POST
        item_id = str(data.get('item_id'))
        quantity = int(data.get('quantity', 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Invalid request parameters'}, status=400)

    cart = get_session_cart(request)
    if quantity <= 0:
        cart.pop(item_id, None)
    else:
        cart[item_id] = min(quantity, 20)

    save_session_cart(request, cart)
    summary = calculate_cart_details(cart)

    return JsonResponse({
        'success': True,
        'item_id': item_id,
        'quantity': cart.get(item_id, 0),
        'item_count': summary['item_count'],
        'subtotal': f"{summary['subtotal']:.2f}",
        'tax_amount': f"{summary['tax_amount']:.2f}",
        'total_amount': f"{summary['total_amount']:.2f}",
    })


@require_POST
def clear_cart(request):
    """Clear all items from session cart"""
    request.session['cart'] = {}
    request.session.modified = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'success': True, 'item_count': 0, 'total_amount': '0.00'})
    messages.info(request, "Your cart has been cleared.")
    return redirect('restaurant:cart')


@require_POST
def sync_cart(request):
    """
    Synchronizes client-side localStorage cart with server session.
    Payload: {"cart": {"<item_id>": <quantity>}}
    """
    try:
        data = json.loads(request.body)
        raw_cart = data.get('cart', {})
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)

    clean_cart = {}
    if isinstance(raw_cart, dict):
        for k, v in raw_cart.items():
            try:
                kid = str(int(k))
                q = int(v)
                if q > 0:
                    clean_cart[kid] = min(q, 20)
            except (ValueError, TypeError):
                continue

    save_session_cart(request, clean_cart)
    summary = calculate_cart_details(clean_cart)

    items_payload = []
    for item in summary['items']:
        items_payload.append({
            'id': item['menu_item'].id,
            'name': item['menu_item'].name,
            'price': str(item['price']),
            'quantity': item['quantity'],
            'subtotal': str(item['subtotal']),
            'image_url': item['menu_item'].image_url,
            'is_vegetarian': item['menu_item'].is_vegetarian,
        })

    return JsonResponse({
        'success': True,
        'item_count': summary['item_count'],
        'subtotal': f"{summary['subtotal']:.2f}",
        'tax_amount': f"{summary['tax_amount']:.2f}",
        'total_amount': f"{summary['total_amount']:.2f}",
        'items': items_payload,
    })


@require_POST
def checkout(request):
    """
    Validates form data and session cart, computes true server totals,
    creates Order and OrderItems atomically, clears session cart,
    and redirects to order tracking page.
    """
    form = OrderCheckoutForm(request.POST)
    cart = get_session_cart(request)

    # Optional: if client sent raw cart_json hidden input, fallback/merge
    cart_json_raw = request.POST.get('cart_json')
    if cart_json_raw and not cart:
        try:
            parsed = json.loads(cart_json_raw)
            if isinstance(parsed, dict):
                cart = {str(k): int(v) for k, v in parsed.items() if int(v) > 0}
                save_session_cart(request, cart)
        except Exception:
            pass

    if not cart:
        messages.error(request, "Your cart is empty. Please add items before placing an order.")
        return redirect('restaurant:menu')

    if not form.is_valid():
        cart_summary = calculate_cart_details(cart)
        return render(request, 'restaurant/cart.html', {
            'form': form,
            'cart_summary': cart_summary,
        })

    # Validate availability of items and recompute server totals
    summary = calculate_cart_details(cart)
    if not summary['items']:
        messages.error(request, "All selected items are currently unavailable. Please pick another dish.")
        return redirect('restaurant:menu')

    unavailable = [item['menu_item'].name for item in summary['items'] if not item['is_available']]
    if unavailable:
        messages.error(request, f"Sorry, the following items are currently out of stock: {', '.join(unavailable)}")
        return redirect('restaurant:cart')

    # Atomic creation of Order and OrderItems
    with transaction.atomic():
        order = form.save(commit=False)
        order.subtotal = summary['subtotal']
        order.tax_amount = summary['tax_amount']
        order.total_amount = summary['total_amount']
        order.status = Order.STATUS_RECEIVED
        order.save()

        for item_data in summary['items']:
            OrderItem.objects.create(
                order=order,
                menu_item=item_data['menu_item'],
                quantity=item_data['quantity'],
                price=item_data['price'],
            )

    # Clear Django session cart
    request.session['cart'] = {}
    request.session.modified = True

    messages.success(
        request,
        f"Order #{order.order_number} has been placed successfully! The kitchen has received your ticket."
    )
    return redirect('restaurant:track_order', order_number=order.order_number)


def track_order_view(request, order_number=None):
    """
    Order tracking page showing current progress:
    Received -> Preparing -> Ready -> Completed
    """
    search_input = request.GET.get('order_id', '').strip()
    target_number = order_number or search_input

    order = None
    recent_orders = []

    if target_number:
        # Match by order_number or primary key ID
        order = Order.objects.filter(
            Q(order_number__iexact=target_number) | Q(id__iexact=target_number if target_number.isdigit() else -1)
        ).prefetch_related('items__menu_item').first()

        if not order and target_number:
            messages.warning(request, f"No order found matching '{target_number}'. Please verify your Order ID.")

    if not order:
        # Provide quick sample orders for demonstration
        recent_orders = Order.objects.all().order_by('-created_at')[:5]

    context = {
        'order': order,
        'search_input': target_number or '',
        'recent_orders': recent_orders,
    }
    return render(request, 'restaurant/track_order.html', context)


@require_GET
def order_status_api(request, order_number):
    """
    Real-time status check endpoint used by order tracking page polling.
    """
    order = Order.objects.filter(order_number__iexact=order_number).first()
    if not order:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)

    return JsonResponse({
        'success': True,
        'order_number': order.order_number,
        'status': order.status,
        'status_display': order.get_status_display(),
        'status_badge_class': order.status_badge_class,
        'progress_percentage': order.progress_percentage,
        'updated_at': order.updated_at.strftime('%H:%M:%S'),
    })


def kitchen_dashboard_view(request):
    """
    Kitchen staff dashboard to monitor tickets and advance status:
    Received -> Preparing -> Ready -> Completed.
    """
    status_filter = request.GET.get('status', 'ACTIVE')
    search_query = request.GET.get('q', '').strip()

    orders_qs = Order.objects.prefetch_related('items__menu_item').all()

    if status_filter == 'ACTIVE':
        orders_qs = orders_qs.filter(status__in=[Order.STATUS_RECEIVED, Order.STATUS_PREPARING, Order.STATUS_READY])
    elif status_filter != 'ALL' and status_filter in dict(Order.STATUS_CHOICES):
        orders_qs = orders_qs.filter(status=status_filter)

    if search_query:
        orders_qs = orders_qs.filter(
            Q(order_number__icontains=search_query) |
            Q(table_number__icontains=search_query) |
            Q(customer_name__icontains=search_query)
        )

    # Calculate status counts for dashboard metrics
    counts = {
        'all': Order.objects.count(),
        'received': Order.objects.filter(status=Order.STATUS_RECEIVED).count(),
        'preparing': Order.objects.filter(status=Order.STATUS_PREPARING).count(),
        'ready': Order.objects.filter(status=Order.STATUS_READY).count(),
        'completed': Order.objects.filter(status=Order.STATUS_COMPLETED).count(),
    }
    counts['active'] = counts['received'] + counts['preparing'] + counts['ready']

    context = {
        'orders': orders_qs,
        'counts': counts,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'restaurant/kitchen_dashboard.html', context)


@require_POST
def update_order_status(request, order_number):
    """
    Update order status directly from kitchen dashboard.
    """
    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get('status')

    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status in valid_statuses:
        old_status_display = order.get_status_display()
        order.status = new_status
        order.save()
        messages.success(
            request,
            f"Order #{order.order_number} ({order.table_number}) updated from '{old_status_display}' to '{order.get_status_display()}'."
        )
    else:
        messages.error(request, f"Invalid status selection '{new_status}'.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'badge_class': order.status_badge_class,
        })

    return redirect(request.META.get('HTTP_REFERER') or 'restaurant:kitchen_dashboard')
