from store_app.models import Category # Category modelini store_app'ten import etmeliyiz

def cart_context(request):
    #Sepet
    cart = request.session.get('cart', {})
    total_items = sum(cart.values())
    item_count = len(cart)
    
    #Kategori
    all_categories = Category.objects.all() 
    
    
    return {
        'total_cart_items': total_items,
        'cart_item_count': item_count,
        'all_categories': all_categories, 
    }