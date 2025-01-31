from django.contrib.auth.decorators import login_required
from .forms import ArticleForm
from .models import Article
from django.shortcuts import render, get_object_or_404, redirect
import os
from django.http import JsonResponse

@login_required(login_url='/account/admin-login')
def article_list(request):
    articles = Article.objects.all().order_by('-created_at')  # จัดเรียงจากใหม่ไปเก่า
    return render(request, 'article/article_list.html', {'articles': articles})

@login_required(login_url='/account/admin-login')
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user  # กำหนด user จากที่ล็อกอินอยู่
            article.save()
            return redirect('article_list')
    else:
        form = ArticleForm()

    return render(request, 'article/article_create.html', {'form': form})

@login_required(login_url='/account/admin-login')
def article_edit(request, article_id):
    # ดึงบทความที่ต้องการแก้ไขโดยใช้ article_id
    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)  # ส่งข้อมูลเก่ามาด้วยเพื่ออัปเดต
        if form.is_valid():
            form.save()  # บันทึกข้อมูลที่แก้ไขลงในฐานข้อมูล
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)  # โหลดฟอร์มพร้อมข้อมูลเดิม

    return render(request, 'article/article_edit.html', {'form': form, 'article': article})

def delete_file(file_path):
    # ตรวจสอบว่าไฟล์ที่ต้องการลบมีอยู่จริงในระบบไฟล์หรือไม่
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error while deleting file: {e}")

@login_required(login_url='/account/admin-login')
def article_delete(request, article_id):
    # ดึงบทความตาม ID
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.delete()
        delete_file(article.image.path)
        return JsonResponse({'status': 'success'}, status=200)

    return JsonResponse({'status': 'fail'}, status=400)

@login_required(login_url='/account/admin-login')
def article_detail(request, article_id):
    # ดึงบทความตาม ID
    article = get_object_or_404(Article, id=article_id)
    session_key = f'viewed_post_{article_id}'  # กำหนด session_key เพื่อเก็บข้อมูลการดูบทความ

    # ตรวจสอบว่าผู้ใช้เคยดูบทความนี้แล้วหรือไม่ ถ้ายังไม่เคยดูให้เพิ่มจำนวนการดู
    if not request.session.get(session_key, False):
        request.session[session_key] = True
        article.views += 1
        article.save()

    return render(request, 'article/article_detail.html', {'article': article})