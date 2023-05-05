from django.shortcuts import render, redirect, get_object_or_404
from StoreApp.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    # Check if the user is authenticated
    if current_user.is_authenticated:
        # Check for variations in the POST data
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

        # Check if a cart item with the same product and variations already exists
        cart_item = CartItem.objects.filter(product=product, user=current_user, variations__in=product_variation).first()

        if cart_item:
            # Increment the cart item quantity
            cart_item.quantity += 1
            cart_item.save()
        else:
            # Create a new cart item with the product and variations
            cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            cart_item.variations.set(product_variation)

        return redirect('cart')

    # If the user is not authenticated
    else:
        # Check for variations in the POST data
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

        # Get the cart using the cart_id present in session
        cart_id = _cart_id(request)
        cart, created = Cart.objects.get_or_create(cart_id=cart_id)

        # Check if a cart item with the same product and variations already exists
        cart_item = CartItem.objects.filter(product=product, cart=cart, variations__in=product_variation).first()

        if cart_item:
            # Increment the cart item quantity
            cart_item.quantity += 1
            cart_item.save()
        else:
            # Create a new cart item with the product and variations
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            cart_item.variations.set(product_variation)

        return redirect('cart')


def delete_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
        
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None ):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass # just Ignore


    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items
    }


    return render(request, 'cart/cart.html',context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass # just Ignore


    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items
    }


    return render(request, 'cart/checkout.html',context )