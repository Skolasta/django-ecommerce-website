from django.shortcuts import get_object_or_404, render, redirect
from . import models
from django.db.models import Q
from .models import Product
from .forms import ReviewForm
from django.contrib import messages

# Store main page
def product_list(request):
    products = models.Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'store_app/product_list.html', context)

# Product detail page
def product_detail(request, product_id):
    product = get_object_or_404(models.Product, id=product_id)
    comments = models.Review.objects.filter(product=product).order_by('-created_at')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('core_app:login') 
        
        form = ReviewForm(request.POST)
        # If the form is valid
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product 
            review.user = request.user 
            review.save()
            messages.success(request, 'Your review has been added successfully.')
            return redirect('store_app:product_detail', product_id=product.id)
    
    else:
        form = ReviewForm()
    context = {
        'product': product,
        'comments': comments,
        'form': form, 
    }
    return render(request, 'store_app/product_detail.html', context)

# Search results
def search_results(request):
    query = request.GET.get('q', None) 

    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'store_app/search_results.html', context)

# Cart page
def sepet(request):
    context = {
        'message': 'Cart page is under development.'
    }
    return render(request, 'store_app/sepet.html', context)

# Category list
def category_list(request):
    categories = models.Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'store_app/category_list.html', context)

# List products by category
def products_by_category(request, category_slug):
    try:
        category = models.Category.objects.get(slug=category_slug)
        products = models.Product.objects.filter(category=category)
        context = {
            'category': category,
            'products': products
        }
        return render(request, 'store_app/product_list.html', context)
    except models.Category.DoesNotExist:
        return render(request, 'store_app/product_list.html', {'error': 'Category not found.'}),
