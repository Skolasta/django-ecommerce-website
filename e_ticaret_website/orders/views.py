from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from .models import Order,OrderItem
from . import forms
from django.shortcuts import redirect
from store_app.models import Product
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from iyzipay import ThreedsInitialize
import os
import logging
from django.views.decorators.csrf import csrf_exempt

# Configure logger
logger = logging.getLogger(__name__)

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def checkout_view(request):
    
    cart_session = request.session.get('cart', {})
    if not cart_session:
        messages.warning(request, "Your cart is empty.")
        return redirect('core_app:home')
    
    # Preparing cart items
    cart_items = []
    total_cart_price = 0
    product_ids = cart_session.keys()
    products = Product.objects.filter(id__in=product_ids)
    for product in products:
        quantity = cart_session[str(product.id)]
        total_item_price = product.price * quantity
        total_cart_price += total_item_price
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_item_price,
        })
    
    if request.method == 'POST':                
        # Create form
        form = forms.OrderCreateForm(request.POST)
        
        if form.is_valid():
            # If form is valid
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'pending'
            order.cart_snapshot = request.session.get('cart', {})
            order.save()
            # Iyzico options dictionary
            options = {
                'api_key': os.getenv('IYZICO_API_KEY'),
                'secret_key': os.getenv('IYZICO_SECRET_KEY'),
                'base_url': os.getenv('IYZICO_BASE_URL')
            }
            # UserProfile security check
            try:
                user_profile = request.user.userprofile
                phone_number = user_profile.phone_number or '05000000000'
                city = user_profile.location or 'Istanbul'
            except:
                phone_number = '05000000000'
                city = 'Istanbul'

            # Prepare buyer and address information
            buyer = {
                'id': str(request.user.id),
                'name': form.cleaned_data.get('first_name'),
                'surname': form.cleaned_data.get('last_name'),
                'gsmNumber': phone_number,
                'email': form.cleaned_data.get('email'),
                'ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'city': city,
                'country': 'Turkey',
                'identityNumber': '11111111111',  # TCKN No
                'registrationAddress': form.cleaned_data.get('shipping_address')
            }

            # Prepare shipping address
            shipping_address = {
                'contactName': f"{form.cleaned_data.get('first_name')} {form.cleaned_data.get('last_name')}",
                'city': city,
                'country': 'Turkey',
                'address': form.cleaned_data.get('shipping_address'),
            }

            billing_address = shipping_address

            total_price = 0
            basketItems = []
            cart = request.session.get('cart', {})
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, id=int(product_id))
                item_total_price = product.price * quantity
                total_price += item_total_price

                basket_item = {
                    'id': str(product.id),
                    'name': product.name[:50],  # Iyzico limit
                    'category1': product.category.name[:50] if product.category else 'Genel',
                    'itemType': 'PHYSICAL',
                    'price': f"{item_total_price:.2f}"  # TOTAL PRICE (quantity * price)
                }

                basketItems.append(basket_item)
            
            # Update Order paid_amount
            order.paid_amount = total_price
            order.save()
            
            # Equalize amounts
            assert order.paid_amount == total_price, f"Order amount mismatch: {order.paid_amount} != {total_price}"
            

            # Create a unique conversation ID
            import time
            conversation_id = f"order-{order.id}-{int(time.time())}"
            
            # Get card details from form
            payment_card = {
                'cardHolderName': request.POST.get('card_holder_name', ''),
                'cardNumber': request.POST.get('card_number', '').replace(' ', ''),  # Remove spaces
                'expireMonth': request.POST.get('expire_month', ''),
                'expireYear': request.POST.get('expire_year', ''),
                'cvc': request.POST.get('cvc', '')
            }
            
            # Validate card details
            if not all([payment_card['cardHolderName'], payment_card['cardNumber'], 
                       payment_card['expireMonth'], payment_card['expireYear'], payment_card['cvc']]):
                messages.error(request, "Please fill in all card details.")
                context = {
                    'form': form,
                    'cart_items': cart_items,
                    'total_cart_price': total_cart_price,
                }
                return render(request, 'orders/checkout.html', context)
            
            # Debug: Check amounts
            print(f"DEBUG: Total Price: {total_price:.2f}")
            print(f"DEBUG: Order Paid Amount: {order.paid_amount:.2f}")
            print("DEBUG: Basket Items:")
            basket_total = 0
            for item in basketItems:
                print(f"  - {item['name']}: {item['price']}")
                basket_total += float(item['price'])
            print(f"DEBUG: Basket Total: {basket_total:.2f}")
            
            iyzi_request = {
                'locale': 'tr',
                'conversationId': conversation_id,
                'price': f"{total_price:.2f}",
                'paidPrice': f"{total_price:.2f}",  # Must be the same
                'currency': 'TRY',
                'basketId': str(order.id),
                'paymentGroup': 'PRODUCT',
                'callbackUrl': request.build_absolute_uri(reverse('orders:iyzico_callback')),
                'shippingAddress': shipping_address,
                'billingAddress': billing_address,
                'basketItems': basketItems,
                'buyer': buyer,
                'paymentCard': payment_card,
            }

            # Make the Iyzico API call
            try:
                # Create a ThreedsInitialize instance and call the create method
                threeds_initialize = ThreedsInitialize()
                payment = threeds_initialize.create(iyzi_request, options)
                
                # Read the HTTPResponse object
                if hasattr(payment, 'read'):
                    response_data = payment.read().decode('utf-8')
                    print(f"DEBUG: Response data: {response_data}")
                    
                    # Try to parse JSON
                    import json
                    try:
                        payment_json = json.loads(response_data)
                        print(f"DEBUG: Parsed JSON: {payment_json}")
                        
                        if payment_json.get('status') == 'success':
                            threeds_html_content = payment_json.get('threeDSHtmlContent')
                            if threeds_html_content:
                                print(f"DEBUG: Payment successful - 3DS HTML Content found")
                                
                                # Decode the Base64 encoded HTML
                                import base64
                                decoded_html = base64.b64decode(threeds_html_content).decode('utf-8')
                                print(f"DEBUG: Decoded HTML: {decoded_html[:200]}...")
                                
                                # Return the HTML content directly as HttpResponse
                                from django.http import HttpResponse
                                return HttpResponse(decoded_html)
                            else:
                                print(f"DEBUG: 3DS HTML Content not found")
                        else:
                            error_message = payment_json.get('errorMessage', 'Unknown error')
                            print(f"DEBUG: Iyzico error - Error: {error_message}")
                            messages.error(request, f"Payment error: {error_message}")
                    except json.JSONDecodeError as e:
                        print(f"DEBUG: JSON parse error: {e}")
                        messages.error(request, "Could not parse API response")
                else:
                    print(f"DEBUG: Payment object does not have a read method")
                    messages.error(request, "Could not read API response")
                
                # Return to checkout page on error
                context = {
                    'form': form,
                    'cart_items': cart_items,
                    'total_cart_price': total_cart_price,
                }
                return render(request, 'orders/checkout.html', context)
                
                    
            except Exception as e:
                
                messages.error(request, f"An error occurred during the payment process: {str(e)}")
                context = {
                    'form': form,
                    'cart_items': cart_items,
                    'total_cart_price': total_cart_price,
                }
                return render(request, 'orders/checkout.html', context)
        else:
            # Log errors if the form is invalid
            print(f"DEBUG: Form invalid - Errors: {form.errors}")
            logger.error(f"Form validation error - Errors: {form.errors}")
        # If form is not valid, fall through to render with errors
    else:
        form = forms.OrderCreateForm()
    
    # Common context for both GET requests and POST requests with errors
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }
    return render(request, 'orders/checkout.html', context)


def orders_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Clear the cart on successful payment
    if order.status in ['processing', 'shipped', 'delivered']:
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
            logger.info(f"Cart cleared - Order ID: {order.id}, User: {request.user.username}")
    
    context = {
        'order': order
    }

    return render(request, 'orders/orders_success.html', context)

@csrf_exempt
def iyzico_callback(request):
    if request.method == 'POST':
        conversation_id = request.POST.get('conversationId')
        status = request.POST.get('status')
        
        try:
            # Extract order ID from conversation ID (format: order-{id}-{timestamp})
            if conversation_id and conversation_id.startswith('order-'):
                parts = conversation_id.split('-')
                if len(parts) >= 3:
                    order_id = int(parts[1])
                else:
                    order_id = int(parts[-1])
            else:
                # Fallback for old format
                order_id = int(conversation_id.split('-')[-1])
                
            order = Order.objects.get(id=order_id)
            logger.info(f"Order found - ID: {order_id}")
            
        except (ValueError, Order.DoesNotExist, IndexError) as e:
            logger.error(f"Invalid Order ID - Conversation ID: {conversation_id}, Error: {str(e)}")
            return HttpResponse('Invalid Order ID', status=400)

        if status == 'success':
            logger.info(f"Successful payment callback - Order ID: {order.id}")
            
            # If payment is successful, update the order status
            if order.status == 'pending':
                order.status = 'processing'
                order.save()
                logger.info(f"Order status updated - Order ID: {order.id}, Status: processing")

                # Create OrderItems
                cart_snapshot = order.cart_snapshot
                created_items = 0
                for product_id, quantity in cart_snapshot.items():
                    try:
                        product = Product.objects.get(id=int(product_id))
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )
                        created_items += 1
                    except Product.DoesNotExist:
                        logger.warning(f"Product not found - Product ID: {product_id}")
                        continue
                
                # Clear cart after payment (session might not be available in callback)
                try:
                    if hasattr(request, 'session') and 'cart' in request.session:
                        del request.session['cart']
                        request.session.modified = True
                        request.session.save()
                        logger.info(f"Cart cleared (callback) - Order ID: {order.id}")
                except Exception as e:
                    logger.warning(f"Could not clear cart in callback - Order ID: {order.id}, Error: {e}")
                    # Cart will be cleared in the orders_success view
            
            # Redirect to success html
            return redirect('orders:orders_success', order_id=order.id)
        else:
            logger.warning(f"Failed payment callback - Order ID: {order.id}, Status: {status}")
            
            # Update status if payment failed
            order.status = 'failed'
            order.save()
            return HttpResponse('payment failed', status=200)

    return HttpResponse('Invalid request', status=400)


# Logger'ı yapılandır
logger = logging.getLogger(__name__)

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def checkout_view(request):
    
    cart_session = request.session.get('cart', {})
    if not cart_session:
        messages.warning(request, "Sepetinizde ürün bulunmamaktadır.")
        return redirect('core_app:home')
    
    # Cart itemlerini hazırlama aşaması
    cart_items = []
    total_cart_price = 0
    product_ids = cart_session.keys()
    products = Product.objects.filter(id__in=product_ids)
    for product in products:
        quantity = cart_session[str(product.id)]
        total_item_price = product.price * quantity
        total_cart_price += total_item_price
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_item_price,
        })
    
    if request.method == 'POST':                
        # Form oluşturma
        form = forms.OrderCreateForm(request.POST)
        
        if form.is_valid():
            #Form geçerli ise
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'pending'
            order.cart_snapshot = request.session.get('cart', {})
            order.save()
            # Iyzico options dictionary
            options = {
                'api_key': os.getenv('IYZICO_API_KEY'),
                'secret_key': os.getenv('IYZICO_SECRET_KEY'),
                'base_url': os.getenv('IYZICO_BASE_URL')
            }
            # UserProfile güvenlik kontrolü
            try:
                user_profile = request.user.userprofile
                phone_number = user_profile.phone_number or '05000000000'
                city = user_profile.location or 'Istanbul'
            except:
                phone_number = '05000000000'
                city = 'Istanbul'

            # Kullanıcı bilgilerini ve adresleri hazırlama
            buyer = {
                'id': str(request.user.id),
                'name': form.cleaned_data.get('first_name'),
                'surname': form.cleaned_data.get('last_name'),
                'gsmNumber': phone_number,
                'email': form.cleaned_data.get('email'),
                'ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'city': city,
                'country': 'Turkey',
                'identityNumber': '11111111111',  # TCKN No
                'registrationAddress': form.cleaned_data.get('shipping_address')
            }

            # Gönderim adresini hazırlama
            shipping_address = {
                'contactName': f"{form.cleaned_data.get('first_name')} {form.cleaned_data.get('last_name')}",
                'city': city,
                'country': 'Turkey',
                'address': form.cleaned_data.get('shipping_address'),
            }

            billing_address = shipping_address

            total_price = 0
            basketItems = []
            cart = request.session.get('cart', {})
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, id=int(product_id))
                item_total_price = product.price * quantity
                total_price += item_total_price

                basket_item = {
                    'id': str(product.id),
                    'name': product.name[:50],  # Iyzico limit
                    'category1': product.category.name[:50] if product.category else 'Genel',
                    'itemType': 'PHYSICAL',
                    'price': f"{item_total_price:.2f}"  # TOPLAM FİYAT (quantity * price)
                }

                basketItems.append(basket_item)
            
            # Order paid_amount'u güncelle
            order.paid_amount = total_price
            order.save()
            
            # Tutarları eşitle
            assert order.paid_amount == total_price, f"Order amount mismatch: {order.paid_amount} != {total_price}"
            

            # Benzersiz conversation ID oluştur
            import time
            conversation_id = f"order-{order.id}-{int(time.time())}"
            
            # Kart bilgilerini formdan al
            payment_card = {
                'cardHolderName': request.POST.get('card_holder_name', ''),
                'cardNumber': request.POST.get('card_number', '').replace(' ', ''),  # Boşlukları kaldır
                'expireMonth': request.POST.get('expire_month', ''),
                'expireYear': request.POST.get('expire_year', ''),
                'cvc': request.POST.get('cvc', '')
            }
            
            # Kart bilgilerini doğrula
            if not all([payment_card['cardHolderName'], payment_card['cardNumber'], 
                       payment_card['expireMonth'], payment_card['expireYear'], payment_card['cvc']]):
                messages.error(request, "Lütfen tüm kart bilgilerini doldurun.")
                context = {
                    'form': form,
                    'cart_items': cart_items,
                    'total_cart_price': total_cart_price,
                }
                return render(request, 'orders/checkout.html', context)
            
            # Debug: Tutarları kontrol et
            print(f"DEBUG: Total Price: {total_price:.2f}")
            print(f"DEBUG: Order Paid Amount: {order.paid_amount:.2f}")
            print("DEBUG: Basket Items:")
            basket_total = 0
            for item in basketItems:
                print(f"  - {item['name']}: {item['price']}")
                basket_total += float(item['price'])
            print(f"DEBUG: Basket Total: {basket_total:.2f}")
            
            iyzi_request = {
                'locale': 'tr',
                'conversationId': conversation_id,
                'price': f"{total_price:.2f}",
                'paidPrice': f"{total_price:.2f}",  # Aynı olmalı
                'currency': 'TRY',
                'basketId': str(order.id),
                'paymentGroup': 'PRODUCT',
                'callbackUrl': request.build_absolute_uri(reverse('orders:iyzico_callback')),
                'shippingAddress': shipping_address,
                'billingAddress': billing_address,
                'basketItems': basketItems,
                'buyer': buyer,
                'paymentCard': payment_card,
            }

            # Iyzico API çağrısını yap
            try:
                # ThreedsInitialize instance oluştur ve create metodunu çağır
                threeds_initialize = ThreedsInitialize()
                payment = threeds_initialize.create(iyzi_request, options)
                
                # HTTPResponse objesini okuyalım
                if hasattr(payment, 'read'):
                    response_data = payment.read().decode('utf-8')
                    print(f"DEBUG: Response data: {response_data}")
                    
                    # JSON parse etmeye çalışalım
                    import json
                    try:
                        payment_json = json.loads(response_data)
                        print(f"DEBUG: Parsed JSON: {payment_json}")
                        
                        if payment_json.get('status') == 'success':
                            threeds_html_content = payment_json.get('threeDSHtmlContent')
                            if threeds_html_content:
                                print(f"DEBUG: Ödeme başarılı - 3DS HTML Content bulundu")
                                
                                # Base64 encoded HTML'i decode et
                                import base64
                                decoded_html = base64.b64decode(threeds_html_content).decode('utf-8')
                                print(f"DEBUG: Decoded HTML: {decoded_html[:200]}...")
                                
                                # HTML içeriğini doğrudan HttpResponse olarak döndür
                                from django.http import HttpResponse
                                return HttpResponse(decoded_html)
                            else:
                                print(f"DEBUG: 3DS HTML Content bulunamadı")
                        else:
                            error_message = payment_json.get('errorMessage', 'Bilinmeyen hata')
                            print(f"DEBUG: Iyzico hatası - Error: {error_message}")
                            messages.error(request, f"Ödeme hatası: {error_message}")
                    except json.JSONDecodeError as e:
                        print(f"DEBUG: JSON parse hatası: {e}")
                        messages.error(request, "API yanıtı parse edilemedi")
                else:
                    print(f"DEBUG: Payment objesi read metoduna sahip değil")
                    messages.error(request, "API yanıtı okunamadı")
                
                # Hata durumunda checkout sayfasına geri dön
                context = {
                    'form': form,
                    'cart_items': cart_items,
                    'total_cart_price': total_cart_price,
                }
                return render(request, 'orders/checkout.html', context)
                
                    
            except Exception as e:
                
                messages.error(request, f"Ödeme işlemi sırasında bir hata oluştu: {str(e)}")
                context = {
                    'form': form,
                    'cart_items': cart_items,
                    'total_cart_price': total_cart_price,
                }
                return render(request, 'orders/checkout.html', context)
        else:
            # Form geçerli değilse hataları logla
            print(f"DEBUG: Form geçersiz - Errors: {form.errors}")
            logger.error(f"Form validation hatası - Errors: {form.errors}")
        # If form is not valid, fall through to render with errors
    else:
        form = forms.OrderCreateForm()
    
    # Common context for both GET requests and POST requests with errors
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }
    return render(request, 'orders/checkout.html', context)


def orders_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Ödeme başarılı olduğunda sepeti temizle
    if order.status in ['processing', 'shipped', 'delivered']:
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
            logger.info(f"Sepet temizlendi - Order ID: {order.id}, User: {request.user.username}")
    
    context = {
        'order': order
    }

    return render(request, 'orders/orders_success.html', context)

@csrf_exempt
def iyzico_callback(request):
    if request.method == 'POST':
        conversation_id = request.POST.get('conversationId')
        status = request.POST.get('status')
        
        try:
            # Conversation ID'den order ID'yi çıkar (format: order-{id}-{timestamp})
            if conversation_id and conversation_id.startswith('order-'):
                parts = conversation_id.split('-')
                if len(parts) >= 3:
                    order_id = int(parts[1])
                else:
                    order_id = int(parts[-1])
            else:
                # Eski format için fallback
                order_id = int(conversation_id.split('-')[-1])
                
            order = Order.objects.get(id=order_id)
            logger.info(f"Order bulundu - ID: {order_id}")
            
        except (ValueError, Order.DoesNotExist, IndexError) as e:
            logger.error(f"Geçersiz Order ID - Conversation ID: {conversation_id}, Error: {str(e)}")
            return HttpResponse('Invalid Order ID', status=400)

        if status == 'success':
            logger.info(f"Başarılı ödeme callback'i - Order ID: {order.id}")
            
            # Ödeme başarılıysa, siparişin durumunu güncelle
            if order.status == 'pending':
                order.status = 'processing'
                order.save()
                logger.info(f"Order durumu güncellendi - Order ID: {order.id}, Status: processing")

                # OrderItem'ları oluştur
                cart_snapshot = order.cart_snapshot
                created_items = 0
                for product_id, quantity in cart_snapshot.items():
                    try:
                        product = Product.objects.get(id=int(product_id))
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )
                        created_items += 1
                    except Product.DoesNotExist:
                        logger.warning(f"Product bulunamadı - Product ID: {product_id}")
                        continue
                
                # Ödeme sonrası sepeti temizle (callback'te session olmayabilir)
                try:
                    if hasattr(request, 'session') and 'cart' in request.session:
                        del request.session['cart']
                        request.session.modified = True
                        request.session.save()
                        logger.info(f"Sepet temizlendi (callback) - Order ID: {order.id}")
                except Exception as e:
                    logger.warning(f"Callback'te sepet temizlenemedi - Order ID: {order.id}, Error: {e}")
                    # Sepet orders_success view'ında temizlenecek
            
            #Success html yönlendirme
            return redirect('orders:orders_success', order_id=order.id)
        else:
            logger.warning(f"Başarısız ödeme callback'i - Order ID: {order.id}, Status: {status}")
            
            # Ödeme başarısızsa durumu güncelle
            order.status = 'failed'
            order.save()
            return HttpResponse('payment failed', status=200)

    return HttpResponse('Invalid request', status=400)