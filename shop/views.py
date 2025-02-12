from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View

from django.shortcuts import get_object_or_404
from products.models import Product
from django.db.models import F, Min, Max
from django.shortcuts import render

class ShopListView(ListView):
    model = Product
    template_name = 'shop/home.html'

class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        options = self.object.options.all()

        # ดึงรูปภาพเพิ่มเติมของสินค้า
        images = self.object.images.all()

        # ดึงสีและไซส์ทั้งหมดที่ไม่ซ้ำกัน
        colors = options.values_list("color", flat=True).distinct()
        sizes = options.values_list("size", flat=True).distinct()

        # คำนวณราคาต่ำสุดและสูงสุด
        price_range = options.aggregate(min_price=Min("price"), max_price=Max("price"))
        min_price = price_range["min_price"] or 0  # ตั้งค่า 0 ถ้าไม่มีราคา
        max_price = price_range["max_price"] or 0

        context.update({
            "images": images,
            "colors": colors,
            "sizes": sizes,
            "price": f"{min_price}" if min_price == max_price else f"{min_price} - {max_price}"
        })
        return context

class ProductOptionView(View):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["pk"])
        color = request.GET.get("color", '').strip()
        size = request.GET.get("size", '').strip()

        options = product.options.all()

        # ดึงสีและไซส์ทั้งหมดที่ไม่ซ้ำกัน
        all_colors = options.values_list("color", flat=True).distinct()
        all_sizes = options.values_list("size", flat=True).distinct()

        # ไซส์ที่มีสำหรับสีที่เลือก
        available_sizes = all_sizes # เริ่มต้นให้ไซส์ที่ใช้ได้คือทั้งหมด
        if color:
            available_sizes = list(options.filter(color=color).values_list("size", flat=True).distinct())

        # สีที่มีสำหรับไซส์ี่เลือก
        available_colors = all_colors
        if size:
            available_colors = list(options.filter(size=size).values_list("color", flat=True).distinct())

        # ดึงราคาต่ำสุดและสูงสุดของสินค้า เมื่อมีการกดเลือกยังไม่ครบ 2 อย่างต้องแสดงอันนี้
        price_range = options.aggregate(min_price=Min('price'), max_price=Max('price'))
        min_price = price_range['min_price'] or 0
        max_price = price_range['max_price'] or 0

        # หาราคาและ id ของตัวเลือกที่เลือกจากทั้ง 2 อย่าง
        product_option_id = None
        price = None
        if color and size:
            selected_option = options.filter(color=color, size=size).first()
            if selected_option:
                product_option_id = selected_option.id
                price = selected_option.price

        # ถ้ายังไม่มีการเลือกทั้ง 2 อย่าง ให้ใช้ช่วงราคาสินค้า
        if price is None:
            price = min_price if min_price == max_price else f"{min_price} - {max_price}"

        return render(request, 'shop/partials/product_options.html', {
            "product_id": product.id,
            "product_option_id": product_option_id,
            "all_colors": all_colors,
            "all_sizes": all_sizes,
            "available_colors": available_colors,
            "available_sizes": available_sizes,
            "selected_color": color,
            "selected_size": size,
            "price": price,
        })
