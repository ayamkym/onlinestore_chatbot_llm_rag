

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .ai import get_ai_response

def product_list_view(request):
    # Retrieve and order products
    product_list = Product.objects.all().order_by('-created_at')  # Order by creation date, newest first
    
    # Paginate the products
    paginator = Paginator(product_list, 12)  # Show 9 products per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Render the response
    return render(request, 'shop/product_list.html', {'page_obj': page_obj})

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})


@csrf_exempt
def get_chatbot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')

        # Get AI response
        response, source_documents = get_ai_response(message)

        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)
