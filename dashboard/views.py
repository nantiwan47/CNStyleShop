import time
from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Review, ReviewAnalysis, ReviewSentiment
from django.db import transaction
from django.views.decorators.http import require_POST

@login_required(login_url='/account/admin-login')
def dashboard(request):
    # ดึงข้อมูลการวิเคราะห์ทั้งหมด
    analysis_results = ReviewAnalysis.objects.all().select_related('review').prefetch_related('reviewsentiment_set')

    # ส่งข้อมูลไปยัง template
    context = {
        'analysis_results': analysis_results,
    }
    return render(request, 'dashboard/dashboard.html', context)

def handle_rate_limit(response):
    """ ฟังก์ชันจัดการเมื่อเกิน Rate Limit และการแจ้งเตือนเวลาที่จะรีเซ็ต"""
    headers = response.headers
    remaining_second = int(headers.get('X-Custom-RateLimit-Remaining-second', 256))
    remaining_minute = int(headers.get('X-RateLimit-Remaining-minute', 120))
    remaining_day = int(headers.get('X-RateLimit-Remaining-day', 10000))
    remaining_month = int(headers.get('X-RateLimit-Remaining-month', 100000))

    # กรณีเกินลิมิตในหน่วยวินาที: รอ 1 วินาทีและดำเนินการต่อ
    if remaining_second <= 0:
        time.sleep(1)
        return None

    # กรณีเกินลิมิตในหน่วยนาที, วัน, เดือน: แจ้งเตือนและหยุดการทำงาน (คำนวณเวลาที่เหลือจนกว่า Rate Limit จะรีเซ็ต)
    if remaining_minute <= 0:
        reset_time = datetime.now() + timedelta(minutes=1)
    elif remaining_day <= 0:
        reset_time = datetime.now() + timedelta(days=1)
    elif remaining_month <= 0:
        reset_time = datetime.now() + timedelta(days=30)
    else:
        return None  # ไม่มีลิมิตเกิน

    return f"{reset_time.strftime('%d-%m-%Y %H:%M:%S')}"

def process_review_analysis(session, review, api_url, headers):
    """ฟังก์ชันวิเคราะห์รีวิว"""

    data = {'text': review.comment}

    # เรียกใช้ API ผ่าน session
    response = session.post(api_url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        sentiment = result.get('sentiment', {})
        preprocess = result.get('preprocess', {})

        with transaction.atomic():
            # 1. บันทึกผลลัพธ์การวิเคราะห์ลงใน ReviewAnalysis
            review_analysis = ReviewAnalysis.objects.create(
                review=review,
                score=float(sentiment.get('score', 0.0)),
                polarity=sentiment.get('polarity', 'neutral') or 'neutral'
            )

            pos_words = preprocess.get('pos', [])
            neg_words = preprocess.get('neg', [])

            sentiments = [
                ReviewSentiment(analysis=review_analysis, sentiment_type='positive', word=word)
                     for word in pos_words
            ] + [
                ReviewSentiment(analysis=review_analysis, sentiment_type='negative', word=word)
                     for word in neg_words
            ]

            # 2. บันทึกข้อมูลคำที่แสดงเชิงบวกหรือเชิงลบทั้งหมดในครั้งเดียว
            ReviewSentiment.objects.bulk_create(sentiments)

            # 3. อัปเดตสถานะ analysis_done เป็น True
            review.analysis_done = True
            review.save()

    elif response.status_code == 429:
        # จัดการกรณีเกินลิมิต
        limit_result = handle_rate_limit(response)
        if limit_result:
            return limit_result
    else:
        # กรณี API ตอบกลับผิดพลาดอื่น ๆ
        return JsonResponse({
            'status': 'error',
            'message': f"API returned status code {response.status_code}"
        }, status=response.status_code)

    # ไม่มีข้อผิดพลาดเกิดขึ้น
    return None

@require_POST
def analyze_reviews(request):
    # ดึงคอมเม้นต์ที่ยังไม่วิเคราะห์
    reviews = Review.objects.filter(analysis_done=False)

    # กรณีไม่มีรีวิวที่ต้องวิเคราะห์
    if not reviews.exists():
        messages.success(request, 'ข้อมูลจากการวิเคราะห์รีวิวสินค้าล่าสุดแล้ว')
        return redirect('dashboard')

    api_url = "https://api.aiforthai.in.th/ssense"
    headers = {
        'Apikey': "JqezYBpyzRy5YrTHTTG2uMXorbtvCQ6W"
    }
    # ใช้ Session เพื่อเพิ่มประสิทธิภาพ ลดการเปิด/ปิดการเชื่อมต่อ HTTP
    with requests.Session() as session:
        for review in reviews:
            # เรียกใช้ฟังก์ชันวิเคราะห์รีวิว
            result = process_review_analysis(session, review, api_url, headers)

            # หากเกิดข้อผิดพลาดระหว่างการวิเคราะห์
            if result:
                messages.error(request, f'เกิดข้อผิดพลาดในการวิเคราะห์รีวิว กรูณาลองใหม่อีกครั้งในเวลา: {result}')
                return redirect('dashboard')

    # กรณีวิเคราะห์รีวิวเสร็จสมบูรณ์
    messages.success(request, f'วิเคราะห์รีวิว {len(reviews)} รายการเสร็จสิ้น')
    return redirect('dashboard')


# ทดสอบในการใช้ api แบบหลายๆ รอบ
def test(request):
    api_url = "https://api.aiforthai.in.th/ssense"
    headers = {
        'Apikey': "JqezYBpyzRy5YrTHTTG2uMXorbtvCQ6W"
    }
    text = 'สาขานี้พนักงานน่ารักให้บริการดี'

    data = {'text': text}


    # ใช้ with requests.Session() เพื่อสร้าง session
    with requests.Session() as session:
        for i in range(122):
            print(f"Processing review #{i + 1}...")

            response = session.post(api_url, headers=headers, data=data)
            if response.status_code == 200:
                print(f"Success: {i}")
            elif response.status_code == 429:
                limit_result = handle_rate_limit(response)
                if limit_result:
                    messages.error(request, f'เกิดข้อผิดพลาดในการวิเคราะห์รีวิว กรุณาลองใหม่อีกครั้งในวันและเวลา: {limit_result}')
                    return redirect('dashboard')
            else:
                print(f"Error {response.status_code}: {response.json()}")

    return redirect('dashboard')





