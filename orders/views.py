from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from cart.cart import CartHandler
from .models import Order, OrderItem
from .forms import CheckoutForm


@login_required
def checkout_view(request):
    """Checkout page."""
    cart = CartHandler(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:home')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, instance=request.user)
        if form.is_valid():
            # Save user info
            form.save()
            # Store shipping info in session for order creation
            request.session['shipping_info'] = {
                'address': request.POST.get('address'),
                'city': request.POST.get('city'),
                'country': request.POST.get('country'),
                'zip_code': request.POST.get('zip_code'),
                'phone': request.POST.get('phone'),
            }
            return redirect('orders:create')
    else:
        form = CheckoutForm(instance=request.user)
    
    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def create_order_view(request):
    """Create order from cart."""
    cart = CartHandler(request)
    shipping_info = request.session.get('shipping_info')
    
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('products:home')
    
    if not shipping_info:
        messages.error(request, 'Please complete checkout form.')
        return redirect('orders:checkout')
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_info['address'],
        shipping_city=shipping_info['city'],
        shipping_country=shipping_info['country'],
        shipping_zip_code=shipping_info['zip_code'],
        shipping_phone=shipping_info['phone'],
        payment_method='cash_on_delivery',
    )
    
    # Create order items
    for item in cart.items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_sku=item.product.sku,
            price=item.product.price,
            quantity=item.quantity,
        )
        
        # Reduce stock
        item.product.stock -= item.quantity
        item.product.purchases_count += item.quantity
        item.product.save(update_fields=['stock', 'purchases_count'])
        
        # Track purchase interaction
        from recommendations.models import UserInteraction
        UserInteraction.track_interaction(
            user=request.user,
            product=item.product,
            interaction_type='purchase'
        )
    
    # Calculate totals
    order.calculate_totals()
    order.status = 'processing'
    order.save(update_fields=['status'])
    
    # Clear cart
    cart.clear()
    
    # Clear shipping info
    if 'shipping_info' in request.session:
        del request.session['shipping_info']
    
    messages.success(request, f'Order {order.order_number} placed successfully!')
    return redirect('orders:success', order_number=order.order_number)


@login_required
def order_success_view(request, order_number):
    """Order success page."""
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('products:home')
    
    return render(request, 'orders/success.html', {'order': order})
