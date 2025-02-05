import time
from datetime import datetime, timedelta

import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, F, Max, Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.timezone import now
from django.views import View
from django.views.generic import ListView, TemplateView

from orders.models import Order, OrderItem
from products.models import Product
from .models import Review, ReviewAnalysis, ReviewSentiment


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
                product=review.product,
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

class AnalyzeReviewsView(View):
    def post(self, request, *args, **kwargs):
        # ดึงคอมเม้นต์ที่ยังไม่วิเคราะห์
        reviews = Review.objects.filter(analysis_done=False)

        # ถ้าไม่มีรีวิวที่ต้องวิเคราะห์
        if not reviews.exists():
            messages.info(request, 'ข้อมูลจากการวิเคราะห์รีวิวสินค้าล่าสุดแล้ว')
            return redirect('dashboard')

        api_url = "https://api.aiforthai.in.th/ssense"
        headers = {
            'Apikey': "JqezYBpyzRy5YrTHTTG2uMXorbtvCQ6W"
        }

        # ใช้ Session เพื่อลดการเปิด/ปิด HTTP Connection
        with requests.Session() as session:
            for review in reviews:
                # ประมวลผลการวิเคราะห์
                result = process_review_analysis(session, review, api_url, headers)

                # หากเกิดข้อผิดพลาด
                if result:
                    messages.error(request, f'เกิดข้อผิดพลาดในการวิเคราะห์รีวิว กรุณาลองใหม่อีกครั้งในเวลา: {result}')
                    return redirect('dashboard')

        # วิเคราะห์รีวิวเสร็จสมบูรณ์
        messages.success(request, f'วิเคราะห์รีวิว {reviews.count()} รายการเสร็จสิ้น')
        return redirect('dashboard')

class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'admin_login'
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = now().date()

        # 1. คำนวณยอดขายที่ status = 'completed' ของเดือนปัจจุบัน
        total_sales = Order.objects.filter(
            status="completed",
            order_date__year=today.year,   # เฉพาะปีปัจจุบัน
            order_date__month=today.month, # เฉพาะเดือนปัจจุบัน
        ).aggregate(Sum("total_price"))["total_price__sum"] or 0

        # 2. จำนวนสินค้าทั้งหมด
        total_products = Product.objects.count()

        # 3. จำนวนออเดอร์วันนี้
        orders_today = Order.objects.filter(order_date__date=today).count()

        # 4. หมวดหมู่สินค้าที่ขายดีที่สุดในเดือนนี้ (กี่ชิ้น)
        best_category = (
            OrderItem.objects.filter(
                order__status="completed",
                order__order_date__year=today.year, # เฉพาะปีปัจจุบัน
                order__order_date__month=today.month # เฉพาะเดือนปัจจุบัน
            )
            .select_related('product') # ดึงข้อมูล Product มาพร้อมกัน ผ่านฟิลด์ product ของตาราง OrderItem
            .values(category=F("product__category")) # ดึง category จาก Product แล้วเปลี่ยนชื่อคอลัมน์เป็น category
            .annotate(total_quantity=Sum("quantity")) # รวมจำนวนสินค้าที่ขายได้ ตามหมวดหมู่
            .order_by("-total_quantity")  # เรียงจากมากไปน้อย
        )

        # #ับจำนวนรีวิวที่ยังไม่ได้วิเคราะห์
        unprocessed_review_count = Review.objects.filter(analysis_done=False).count()

        # หาวันที่มีการวิเคราะห์ล่าสุด
        latest_analysis_time = ReviewAnalysis.objects.aggregate(latest_time=Max('created_at'))['latest_time']

        # 5. วิเคราะห์ความคิดเห็นสินค้าทั้งหมด
        total_reviews_product = ReviewAnalysis.objects.count()  # นับจำนวนความคิดเห็นทั้งหมด

        # นับจำนวนรีวิวแต่ละประเภท (positive, neutral, negative)
        sentiment_counts = ReviewAnalysis.objects.values('polarity').annotate(count=Count('id'))

        # สร้าง dictionary สำหรับเก็บเปอร์เซ็นต์
        sentiment_percentages = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }

        # ถ้ามีรีวิวทั้งหมด
        if total_reviews_product > 0:
            for item in sentiment_counts:
                sentiment_percentages[item['polarity']] = round((item['count'] / total_reviews_product) * 100, 2)

        # 6. วิเคราะห์ความคิดเห็นตามประเภทสินค้า
        review_summary = Product.objects.values('category').annotate(
            total_reviews=Count('analyses'),
            positive_reviews=Count('analyses', filter=Q(analyses__polarity='positive')),
            negative_reviews=Count('analyses', filter=Q(analyses__polarity='negative')),
            neutral_reviews=Count('analyses', filter=Q(analyses__polarity='neutral'))
        ).order_by('category')

        result = []
        for item in review_summary:
            total_reviews = item['total_reviews']

            # คำนวณเปอร์เซ็นต์
            positive_percentage = (item['positive_reviews'] / total_reviews) * 100 if total_reviews > 0 else 0
            negative_percentage = (item['negative_reviews'] / total_reviews) * 100 if total_reviews > 0 else 0
            neutral_percentage = (item['neutral_reviews'] / total_reviews) * 100 if total_reviews > 0 else 0

            result.append({
                'category': item['category'],
                'total_reviews': total_reviews,
                'positive_reviews': item['positive_reviews'],
                'negative_reviews': item['negative_reviews'],
                'neutral_reviews': item['neutral_reviews'],

                'positive_percentage': round(positive_percentage, 2),  # ปัดเศษเป็นทศนิยม 2 ตำแหน่ง
                'negative_percentage': round(negative_percentage, 2),  # ปัดเศษเป็นทศนิยม 2 ตำแหน่ง
                'neutral_percentage': round(neutral_percentage, 2)  # ปัดเศษเป็นทศนิยม 2 ตำแหน่ง
            })

        context.update(
            {
                "total_sales": total_sales,
                "total_products": total_products,
                "orders_today": orders_today,
                "best_category": best_category,
                "total_reviews_product": total_reviews_product,
                "unprocessed_review_count": unprocessed_review_count,
                "latest_analysis_time": latest_analysis_time,
                "sentiment_percentages": dict(sentiment_percentages),
                "result": result,

            }
        )
        return context

class ProductAnalysisListView(LoginRequiredMixin, ListView):
    login_url = 'admin_login'
    model = Product
    template_name = 'dashboard/product_analysis.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        queryset = Product.objects.annotate(
            total_reviews=Count('product_reviews')
        ).filter(total_reviews__gt=0).prefetch_related(
            'product_reviews',  # ดึงรีวิวทั้งหมดของสินค้า
            'analyses',                 # ดึงการวิเคราะห์ของแต่ละสินค้า
            'analyses__sentiments'      # ดึงคำเชิงบวก/ลบ จากการวิเคราะห์
        )

        # รับค่าค้นหาจาก Query Parameters
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |  # ค้นหาตามรหัสสินค้า
                Q(name__icontains=search_query) | # ค้นหาตามชื่อสินค้า
                Q(analyses__sentiments__word__icontains=search_query)  # ค้นหาจากคำเชิงบวก/ลบ
            )

        return queryset.order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # คำนวณข้อมูลรีวิวและการวิเคราะห์
        for product in context['products']:
            reviews = product.product_reviews.all()  # ดึงรีวิวทั้งหมดของสินค้า
            total_reviews = reviews.count()

            # คำนวณเปอร์เซ็นต์ของรีวิวที่เป็นบวก, ลบ, และเป็นกลาง
            analysis = product.analyses.all()  # ดึงการวิเคราะห์ของสินค้า
            positive_reviews = analysis.filter(polarity='positive').count()
            negative_reviews = analysis.filter(polarity='negative').count()
            neutral_reviews = analysis.filter(polarity='neutral').count()

            positive_percentage = (positive_reviews / total_reviews * 100) if total_reviews else 0
            negative_percentage = (negative_reviews / total_reviews * 100) if total_reviews else 0
            neutral_percentage = (neutral_reviews / total_reviews * 100) if total_reviews else 0

            # คำนวณคำเชิงบวกและเชิงลบ
            positive_words = {}
            negative_words = {}

            for analysis_item in analysis:  # ใช้ข้อมูลจากที่โหลดมาแล้ว
                for sentiment in analysis_item.sentiments.all():  # ดึงคำเชิงบวก/ลบจาก prefetch_related
                    if sentiment.sentiment_type == 'positive':
                        positive_words[sentiment.word] = positive_words.get(sentiment.word, 0) + 1
                    else:
                        negative_words[sentiment.word] = negative_words.get(sentiment.word, 0) + 1

            # เก็บข้อมูลลงใน product
            product.review_data = {
                'total_reviews': total_reviews,
                'positive_percentage': positive_percentage,
                'negative_percentage': negative_percentage,
                'neutral_percentage': neutral_percentage,
                'positive_word_count': positive_words,
                'negative_word_count': negative_words,
            }

        query_params = self.request.GET.copy()  # คัดลอก query parameters
        query_params.pop('page', None)  # ลบพารามิเตอร์ 'page' ถ้ามี
        context['query_params'] = query_params.urlencode()  # แปลงเป็น query string

        return context


# ทดสอบในการใช้ api แบบหลายๆ รอบ
def test(request):
    api_url = "https://api.aiforthai.in.th/ssense"
    headers = {
        'Apikey': "JqezYBpyzRy5YrTHTTG2uMXorbtvCQ6W"
    }
    text = 'สาขานี้พนักงานน่ารักให้บริการดี'

    data = {'text': text}

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





