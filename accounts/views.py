from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib import messages
from .forms import UserRegisterForm, AdminRegistrationForm, UserProfileForm
from .models import UserProfile
from typing import cast

class UserRegisterView(CreateView):
    model = UserProfile
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        # ดึงค่า next จาก URL หากมี
        next_url = self.request.GET.get('next')

        # ตรวจสอบ role ของผู้ใช้
        if self.request.user.role == 'user':
            if next_url:
                return next_url  # ไปที่หน้าที่ผู้ใช้พยายามเข้าถึง
            else:
                return reverse_lazy('home')

        # เพิ่มข้อความแจ้งเตือน
        messages.error(self.request, "กรุณาล็อกอินด้วยบัญชีผู้ใช้")
        return reverse_lazy('login')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')

class AdminRegisterView(CreateView):
    model = UserProfile
    form_class = AdminRegistrationForm
    template_name = 'accounts/admin_register.html'
    success_url = reverse_lazy('admin_login')

    def form_valid(self, form):
        user = form.save(commit=False)  # ไม่บันทึกข้อมูลในฐานข้อมูลก่อน
        user.role = 'admin'  # กำหนด role เป็น admin
        user.is_staff = True  # ให้เข้าถึง admin panel
        user.is_superuser = True  # กำหนดให้เป็น superuser
        user.save()  # บันทึกข้อมูล
        return super().form_valid(form)

class AdminLoginView(LoginView):
    template_name = 'accounts/admin_login.html'

    def get_success_url(self) -> str:
        # ดึงค่า next จาก URL หากมี
        next_url = self.request.GET.get('next')

        # บอก IDE ว่า self.request.user คือ UserProfile
        user = cast(UserProfile, self.request.user)

        # ตรวจสอบ role ของผู้ใช้
        if user.role == 'admin':
            if next_url:
                return next_url  # ไปที่หน้าที่ผู้ใช้พยายามเข้าถึง
            else:
                return reverse_lazy('dashboard')

        # เพิ่มข้อความแจ้งเตือน และกลับไปหน้า login ของแอดมิน
        messages.error(self.request, "กรุณาล็อกอินด้วยบัญชีแอดมิน")
        return reverse_lazy('admin_login')

class AdminLogoutView(LogoutView):
    next_page = reverse_lazy('admin_login')

class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'accounts/profile.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        # เมื่อฟอร์มถูกบันทึกสำเร็จ
        messages.success(self.request, "ข้อมูล Profile ถูกอัปเดตเรียบร้อยแล้ว")
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user  # ให้โหลดข้อมูลของ user ที่ล็อกอินอยู่

