from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Product
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import csv

# ====================
# Inventory Views
# ====================

@login_required
def product_list(request):
    products = Product.objects.all()

    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_filter:
        products = products.filter(category=category_filter)

    categories = Product.objects.values_list('category', flat=True).distinct()

    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories
    })

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        category = request.POST['category']
        price = float(request.POST['price'])
        quantity = int(request.POST['quantity'])
        low_stock_threshold = int(request.POST['low_stock_threshold'])

        Product.objects.create(
            name=name,
            category=category,
            price=price,
            quantity=quantity,
            low_stock_threshold=low_stock_threshold
        )
        return redirect('product_list')

    return render(request, 'add_product.html')


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST['name']
        product.category = request.POST['category']
        product.price = float(request.POST['price'])
        product.quantity = int(request.POST['quantity'])
        product.low_stock_threshold = int(request.POST['low_stock_threshold'])
        product.save()
        return redirect('product_list')

    return render(request, 'edit_product.html', {'product': product})


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product_list')


@login_required
def generate_pdf(request):
    products = Product.objects.all()
    template = get_template('product_pdf.html')
    html = template.render({'products': products})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="product_list.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_list.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Price', 'Quantity', 'Low Stock'])

    products = Product.objects.all()
    for p in products:
        writer.writerow([p.name, p.category, p.price, p.quantity, p.low_stock_threshold])

    return response


# ====================
# Auth Views
# ====================

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('product_list')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
