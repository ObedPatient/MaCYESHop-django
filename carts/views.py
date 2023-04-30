from django.shortcuts import render, redirect, get_object_or_404
from StoreApp.models import Product, Variation
from carts.models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
def _cart_id(request):
    cart= request.session.session_key
    if not cart:
        cart= request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try: 
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist: 
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    for item in cart_items:
        existing_variations = item.variations.all()
        if existing_variations.count() == len(product_variation):
            matches = existing_variations.filter(id__in=[v.id for v in product_variation])
            if matches.count() == len(product_variation):
                # The cart item with the same product and variations already exists, so just update the quantity
                item.quantity += 1
                item.save()
                return redirect('cart')

    # No matching cart item was found, so create a new one
    cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
    if len(product_variation) > 0:
        cart_item.variations.clear()
        cart_item.variations.add(*product_variation)
    cart_item.save() 

    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }

    return render(request, 'cart/cart.html', context)

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item= CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')
