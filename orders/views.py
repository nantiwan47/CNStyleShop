from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'orders/order_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)  # ดึงข้อมูลคำสั่งซื้อโดยใช้ ID
    return render(request, 'orders/order_detail.html', {'order': order})
