import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.core.management import call_command
from .models import Product
from .ai import get_ai_response

def product_list_view(request):
    """
    Display a paginated list of products.
    """
    product_list = Product.objects.all().order_by('-created_at')  # Order by creation date, newest first
    
    paginator = Paginator(product_list, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shop/product_list.html', {'page_obj': page_obj})

def product_detail_view(request, product_id):
    """
    Display detailed information about a single product.
    """
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

@csrf_exempt
def get_chatbot_response(request):
    """
    Handle POST requests for chatbot responses.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        session_id = request.session.session_key  # Get session ID from Django session

        response = get_ai_response(message, session_id, request)

        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def create_superuser_view(request):
    """
    Create a superuser via a view.
    """
    call_command('create_superuser')
    return HttpResponse('Superuser created')
