from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AdminOnlyMiddleware:
    """Middleware ที่ป้องกันไม่ให้ผู้ใช้ทั่วไปเข้า `/admin/`"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ถ้า URL เริ่มต้นด้วย `/admin/`
        if request.path.startswith('/admin/'):
            # ตรวจสอบว่าผู้ใช้ล็อกอินหรือไม่
            if request.user.is_authenticated:
                # ถ้าล็อกอินแล้วแต่ไม่ใช่แอดมิน → Redirect ไปหน้า Admin Login
                if request.user.role != 'admin':
                    messages.error(request, "คุณไม่มีสิทธิ์เข้าใช้งานหน้าสำหรับแอดมิน กรุณาล็อกอินด้วยบัญชีแอดมิน")
                    return redirect(reverse('admin_login'))

        # ถ้าผ่านการตรวจสอบแล้ว → ให้ request ไปยัง view ตามปกติ และถ้ายังไม่ได้ล็อกอิน ปล่อยให้ระบบจัดการเปลี่ยนเส้นทางเองใน view
        return self.get_response(request)


class RedirectCartAddMiddleware:
    """Middleware สำหรับเปลี่ยนเส้นทางเมื่อผู้ใช้ล็อกอินสำเร็จ และมี next เป็น /cart/add/"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ตรวจสอบเมื่อผู้ใช้ล็อกอินสำเร็จ และมี next ใน URL
        response = self.get_response(request)

        # ตรวจสอบเมื่อผู้ใช้ล็อกอินแล้ว และมี next ที่เป็น /cart/add/
        if request.user.is_authenticated and 'next' in request.GET:
            next_url = request.GET['next']

            # ถ้า next_url เป็น /cart/add/ ให้เปลี่ยนไปที่หน้า product_detail
            if next_url.startswith('/cart/add/'):
                product_id = next_url.split('/')[-1]
                messages.info(request, f'กรุณาทำการเพิ่มสินค้าลงรถเข็นใหม่อีกครั้ง')
                return redirect(reverse('product_detail', kwargs={'pk': product_id}))  # เปลี่ยนไปที่หน้ารายละเอียดสินค้า
        return response
