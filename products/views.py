import os
from django.db.models import Min, Max
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from .models import Product, ProductOption, ProductImage
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required(login_url='/account/admin-login')
def dashboard(request):
    return render(request, 'products/dashboard.html')

@login_required(login_url='/account/admin-login')
def product_list(request):
    # รับค่าคำค้นหาจาก URL
    query = request.GET.get('search', '').strip()  # กรณีที่ไม่มีคำค้นหาจะเป็นค่าว่าง และตัดช่องว่างหัวท้ายออก
    category = request.GET.get('category', '')

    # ดึงข้อมูลสินค้าทั้งหมดพร้อมราคาต่ำสุดและสูงสุด
    products = Product.objects.annotate(
        min_price=Min('options__price'),
        max_price=Max('options__price'),
    )

    # กรองข้อมูลตามคำค้นหาและประเภท
    if query:
        products = products.filter(Q(name__icontains=query))  # ค้นหาตามชื่อสินค้า
    if category:
        products = products.filter(category=category)  # กรองตามหมวดหมู่

    # จัดเรียงสินค้าตาม ID จากล่าสุดไปเก่าสุด
    products = products.order_by('-id')

    # แบ่งเพจ - 10 รายการต่อหน้า
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page') # รับหมายเลขหน้าจาก URL
    page_obj = paginator.get_page(page_number)  # สร้าง object ของหน้าที่กำลังดู

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj, # ส่งข้อมูลหน้าปัจจุบันไปที่ Template
        'query': query,
        'selected_category': category,
        'category_choices': Product.CATEGORY_CHOICES,  # ส่ง Choices ของ ตาราง Product ไปยัง Template
    })

@login_required(login_url='/account/admin-login')
def product_create(request):
    if request.method == 'POST':
        # ดึงข้อมูลสินค้าจากฟอร์ม
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        cover_image = request.FILES.get('cover_image')

        # บันทึกสินค้า
        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            cover_image=cover_image
        )

        # ดึงข้อมูลตัวเลือกสินค้าจากฟอร์ม
        colors = request.POST.getlist('color[]')
        sizes = request.POST.getlist('size[]')
        prices = request.POST.getlist('price[]')

        # บันทึกตัวเลือกสินค้า
        for color, size, price in zip(colors, sizes, prices):
            ProductOption.objects.create(
                product=product,
                color=color,
                size=size,
                price=price
            )

        # ดึงข้อมูลรูปภาพเพิ่มเติมจากฟอร์ม
        image_files = request.FILES.getlist('images[]')

        # บันทึกรูปภาพเพิ่มเติม
        if image_files:
            for image in image_files:
                ProductImage.objects.create(
                    product=product,
                    image=image
                )

        return redirect('product_list')

    return render(request, 'products/product_create.html')

@login_required(login_url='/account/admin-login')
@transaction.atomic
def product_edit(request, product_id):
    # ดึงข้อมูลสินค้าที่ต้องการแก้ไขจากฐานข้อมูลโดยใช้ product_id
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # 1. ดึงข้อมูลสินค้าจากฟอร์ม
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        cover_image = request.FILES.get('cover_image')

        # อัปเดตข้อมูลสินค้า
        product.name = name
        product.description = description
        product.category = category

        if cover_image:
            product.cover_image = cover_image  # อัปเดตรูปภาพหากมีการอัปโหลดรูปปกสินค้าใหม่

        # บันทึกข้อมูลสินค้า
        product.save()

        # ลบตัวเลือกสินค้าเก่าทั้งหมดก่อน แล้วจะเพิ่มใหม่
        ProductOption.objects.filter(product=product).delete()

        # 2. ดึงข้อมูลตัวเลือกสินค้าจากฟอร์ม
        colors = request.POST.getlist('color[]')
        sizes = request.POST.getlist('size[]')
        prices = request.POST.getlist('price[]')

        # ตรวจสอบความถูกต้องของข้อมูลตัวเลือก และเพิ่มข้อมูล
        for color, size, price in zip(colors, sizes, prices):
            if color and size and price:
                ProductOption.objects.create(
                    product=product,
                    color=color,
                    size=size,
                    price=price
                )

        # 3. ดึงข้อมูลรูปภาพเพิ่มเติมใจากฟอร์ม
        new_images = request.FILES.getlist('new_images[]')

        # ถ้ามีรูปภาพใหม่ เพิ่มภาพใหม่ลงในฐานข้อมูล
        if new_images:
            for image in new_images:
                ProductImage.objects.create(
                    product=product,
                    image=image
                )

        return redirect('product_list')

    # ดึงข้อมูลตัวเลือกสินค้าและรูปภาพเพิ่มเติมเพื่อแสดงในฟอร์ม
    options = product.options.all()
    images = list(product.images.all())  # แปลง QuerySet เป็น List

    # เติมให้รูปภาพแสดงครบ 4 ช่องในฟอร์ม หากยังมีไม่ครบ
    while len(images) < 4:
        images.append(None)

    # ข้อมูลที่จะส่งไปยังเทมเพลต
    context = {
        'product': product,
        'options': options,
        'images': images,
    }
    return render(request, 'products/product_edit.html', context)

def delete_image(request, image_id):
    if request.method == 'DELETE':
        # ตรวจสอบว่าเป็นคำขอจาก HTMX หรือไม่
        if request.headers.get('HX-Request'):
            # ลบภาพ
            image = get_object_or_404(ProductImage, id=image_id)

            image_file_path = image.image.path
            image.delete()  # ลบจากฐานข้อมูล

            # ลบไฟล์จากระบบไฟล์
            try:
                os.remove(image_file_path)
            except:
                pass  # ถ้าไม่สามารถลบไฟล์ได้ก็ไม่ต้องทำอะไร

            # เมื่อคำขอมาจาก HTMX ส่ง HTML ใหม่ที่แทนที่ content ของ #images_preview
            return HttpResponse('<span class="text-gray-400">รูปภาพ</span>')  # แสดงข้อความ placeholder

        else:
            # ถ้าไม่ใช่คำขอจาก HTMX ให้ส่งคำตอบอื่นๆ ตามปกติ
            return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def delete_file(file_path):
    # ตรวจสอบว่าไฟล์ที่ต้องการลบมีอยู่จริงในระบบไฟล์หรือไม่
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error while deleting file: {e}")

@login_required(login_url='/account/admin-login')
@transaction.atomic
def product_delete(request, product_id):
    # ดึงข้อมูลสินค้าที่ต้องการลบ
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':

        # ลบรูปภาพหลักของสินค้า (cover_image) ออกจากระบบไฟล์ (filesystem) ของเซิร์ฟเวอร์
        if product.cover_image:
            # เรียกฟังก์ชัน delete_file เพื่อลบไฟล์รูปภาพปกสินค้า
            delete_file(product.cover_image.path)

        # ลบตัวเลือกสินค้าที่เกี่ยวข้อง
        ProductOption.objects.filter(product=product).delete()

        # ลบรูปภาพที่เกี่ยวข้องจาก ProductImage ออกจากระบบไฟล์ (filesystem) ของเซิร์ฟเวอร์
        product_images = ProductImage.objects.filter(product=product)
        for image in product_images:
            delete_file(image.image.path)

        # ลบสินค้าออกจากฐานข้อมูล
        product.delete()

        return JsonResponse({'status': 'success'}, status=200)

    return JsonResponse({'status': 'fail'}, status=400)

