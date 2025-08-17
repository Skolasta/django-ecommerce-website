from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from store_app.models import Product 
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from store_app.models import Product 
from django.views.decorators.http import require_POST # To accept only POST requests

@require_POST # Only POST requests
@login_required(login_url='/login/')
def add_to_cart(request):
    # Get cart from session, or create an empty dictionary if it doesn't exist
    cart = request.session.get('cart', {})
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    if product_id:
        # If this product is in the cart, increase its quantity, otherwise add it as a new item
        cart[product_id] = cart.get(product_id, 0) + quantity
        request.session['cart'] = cart
        request.session.modified = True

    # AJAX check
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_count = len(cart)
        return JsonResponse({
            'status': 'success', 
            'message': 'Product added to cart!',
            'cart_item_count': item_count
        })
    
    # If a normal form was submitted
    return redirect('cart:view_cart')


# Only POST requests
@require_POST
@login_required(login_url='/login/')
def remove_from_cart(request):
    # Get cart from session, or create an empty dictionary if it doesn't exist
    cart = request.session.get('cart', {})
    product_id = request.POST.get('product_id')

    # If the product ID exists in the cart, delete it
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart:view_cart')


@login_required(login_url='/login/')
def view_cart(request):
    # Get the simple cart dictionary from the session 
    cart_session = request.session.get('cart', {})
    
    # The cart list we will send to the template
    cart_items = []
    total_cart_price = 0

    # Fetch product information from the database in a single query using the product IDs in the cart
    product_ids = cart_session.keys()
    products = Product.objects.filter(id__in=product_ids)

    # Let's loop through the fetched products and create a list for the template
    for product in products:
        quantity = cart_session[str(product.id)]
        total_item_price = product.price * quantity
        
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_item_price,
        })
        
        total_cart_price += total_item_price
    
    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }
    
    return render(request, 'cart/cart_detail.html', context)



# Sadece POST istekleri
@require_POST
@login_required(login_url='/login/')
def remove_from_cart(request):
    # Session'dan sepeti al, eğer yoksa boş bir sözlük oluştur
    cart = request.session.get('cart', {})
    product_id = request.POST.get('product_id')

    # Eğer ürün ID'si sepette varsa sil
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart:view_cart')


@login_required(login_url='/login/')
def view_cart(request):
    # Session'dan basit sepet sözlüğünü al 
    cart_session = request.session.get('cart', {})
    
    # Template'e göndereceğimiz sepet listesi
    cart_items = []
    total_cart_price = 0

    # Sepetteki ürün ID'lerini kullanarak veritabanından ürün bilgilerini tek bir sorguda çek
    product_ids = cart_session.keys()
    products = Product.objects.filter(id__in=product_ids)

    # Çektiğimiz ürünler üzerinden döngüye girip template için liste oluşturalım
    for product in products:
        quantity = cart_session[str(product.id)]
        total_item_price = product.price * quantity
        
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_item_price,
        })
        
        total_cart_price += total_item_price
    
    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }
    
    return render(request, 'cart/cart_detail.html', context)