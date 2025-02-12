from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.views import View

from cart.models import Cart
from dashboard.models import Review
from products.models import Product, ProductOption
from .forms import OrderFilterForm
from .models import Order, OrderItem
from .forms import OrderForm

from django.http import HttpResponseRedirect



class OrderListView(LoginRequiredMixin, ListView):
    login_url = 'admin_login'
    model = Order
    template_name = 'orders/admin/order_list.html'
    paginate_by = 10 # แบ่งหน้า 10 รายการ

    def get_queryset(self):
        # รับค่าค้นหาจาก URL
        query = self.request.GET.get('search', '').strip()  # กรณีที่ไม่มีคำค้นหาจะเป็นค่าว่าง และตัดช่องว่างหัวท้ายออก
        status_filter = self.request.GET.get('status', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')


        orders = Order.objects.all().order_by('-id') # จัดเรียงจากใหม่ไปเก่า

        if query:
            orders = orders.filter(
                Q(order_code__icontains=query) |
                Q(full_name__icontains=query) |
                Q(phone__icontains=query)
            )

        if status_filter:
            orders = orders.filter(status=status_filter)

        if date_from and date_to:
            orders = orders.filter(order_date__date__range=[date_from, date_to])
        elif date_from:
            orders = orders.filter(order_date__date__gte=date_from)  # ค้นหาตั้งแต่วันที่เลือกขึ้นไป
        elif date_to:
            orders = orders.filter(order_date__date__lte=date_to)  # ค้นหาตั้งแต่วันที่เลือกลงไป

        return orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query_params = self.request.GET.copy()  # คัดลอก query parameters
        query_params.pop('page', None)  # ลบพารามิเตอร์ 'page' ถ้ามีอยู่ เพื่อป้องกันค่าหน้าเก่าถูกส่งไป

        context['form'] = OrderFilterForm(self.request.GET)
        context['query'] = self.request.GET.get('search', '').strip()
        context['status_filter'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['query_params'] = query_params.urlencode()  # แปลงเป็น query string ที่ใช้ใน URL

        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    login_url = 'admin_login'
    model = Order
    template_name = 'orders/admin/order_detail.html'
    context_object_name = 'order'

class BuyNowView(LoginRequiredMixin, FormView):
    login_url = 'login'
    template_name = 'orders/user/checkout.html'
    form_class = OrderForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.request.GET.get("product_id")
        option_id = self.request.GET.get("option_id")
        quantity = int(self.request.GET.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)
        option = get_object_or_404(ProductOption, id=option_id)

        total_price = option.price * quantity
        user = self.request.user

        context.update({
            "user": user,
            "items": [{
                "product": product,
                "product_option": option,
                "quantity": quantity,
                "unit_price": option.price,
                "item_price": total_price, # คือ ราคารวมของแต่ละสินค้า
            }],
            "total_price": total_price, # ราคารวมทั้งหมด
            "is_buynow": True,
            "product": product,
        })

        return context

    def form_valid(self, form):
        """ สร้าง Order และ OrderItem แล้ว Redirect ไปยังหน้าชำระเงิน """
        option_id = self.request.POST.get("option_id")
        quantity = int(self.request.POST.get("quantity", 1))

        option = get_object_or_404(ProductOption, id=option_id)
        product = option.product
        total_price = option.price * quantity

        order = form.save(commit=False)
        order.user = self.request.user
        order.total_price = total_price
        order.status = "pending"
        order.save()

        # เพิ่มสินค้าเข้า OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            color=option.color,
            size=option.size,
            quantity=quantity,
            unit_price=option.price,
        )

        return HttpResponseRedirect(reverse_lazy('payment', kwargs={'order_id': order.id}))

class CartCheckoutView(LoginRequiredMixin, FormView):
    login_url = 'login'
    template_name = 'orders/user/checkout.html'
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        """ ตรวจสอบตะกร้า หากไม่มีสินค้าให้ redirect ไปยังหน้าตะกร้า """
        user = self.request.user
        cart = Cart.objects.get(user=user)

        if not cart.items.exists():
            return redirect('cart_detail')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        cart = Cart.objects.get(user=user)

        context.update({
            "user": user,
            "items": cart.items.all(),
            "total_price": cart.get_total_price(),  # ราคารวมทั้งหมด
        })

        return context


    def form_valid(self, form):
        user = self.request.user
        cart = Cart.objects.get(user=user)

        # สร้างคำสั่งซื้อ
        order = form.save(commit=False)
        order.user = user
        order.total_price = cart.get_total_price()
        order.status = "pending"
        order.save()

        # บันทึกสินค้าจาก Cart ไปยัง OrderItem
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                color=item.product_option.color,
                size=item.product_option.size,
                quantity=item.quantity,
                unit_price=item.product_option.price,
            )

        # ลบสินค้าออกจากตะกร้า
        cart.items.all().delete()

        return HttpResponseRedirect(reverse_lazy('payment', kwargs={'order_id': order.id}))

class PaymentView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, order_id):
        """ แสดงหน้าชำระเงินพร้อมรายละเอียดคำสั่งซื้อ """
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)

        context = {
            "order": order,
            "order_items": order_items,
        }
        return render(request, "orders/user/payment.html", context)

    def post(self, request, order_id):
        """ อัพโหลดสลิปและเปลี่ยนสถานะเป็น 'จ่ายแล้ว' """
        order = get_object_or_404(Order, id=order_id, user=request.user)
        slip = request.FILES.get("payment_image")

        if slip:
            order.payment_image = slip
            order.status = "paid"  # เปลี่ยนสถานะเป็นจ่ายแล้ว
            order.save()
            messages.success(request, "อัปโหลดสลิปสำเร็จ! คำสั่งซื้อของคุณได้รับการชำระเงินแล้ว")
            return redirect("home")

        messages.error(request, "กรุณาแนบสลิปการโอนเงิน")
        return redirect("payment", order_id=order.id)

class MyOrdersView(LoginRequiredMixin, TemplateView):
    template_name = "orders/user/my_orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["pending_orders"] = Order.objects.filter(user=user, status="pending")
        context["paid_orders"] = Order.objects.filter(user=user, status="paid")
        context["completed_orders"] = Order.objects.filter(user=user, status="completed")
        context["cancelled_orders"] = Order.objects.filter(user=user, status="cancelled")
        context["reviews"] = Review.objects.filter(user=user)
        return context
