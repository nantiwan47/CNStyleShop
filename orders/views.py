from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView

from .forms import OrderFilterForm
from .models import Order


class OrderListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('admin_login')
    model = Order
    template_name = 'orders/order_list.html'
    paginate_by = 1 # แบ่งหน้า 10 รายการ

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
    login_url = reverse_lazy('admin_login')
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
