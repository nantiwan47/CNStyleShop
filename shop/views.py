from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from articles.models import Article
from products.models import Product
from django.db.models import F



class ShopListView(ListView):
    model = Product
    template_name = 'shop/home.html'


class ShopArticleListView(ListView):
    model = Article
    template_name = 'shop/article_list.html'
    context_object_name = 'articles'
    ordering = ['-created_at']
    paginate_by = 10

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'shop/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = f'viewed_article_{self.object.pk}' # กำหนดคีย์ของ session เพื่อเก็บสถานะว่าผู้ใช้เคยดูบทความนี้หรือยัง

        if not self.request.session.get(session_key, False):
            # ถ้ายังไม่เคยดูบทความนี้ ให้เพิ่มจำนวน views
            # ใช้ F('views') + 1 เพื่อเพิ่มค่า views โดยตรงในฐานข้อมูล
            # ป้องกัน Race Condition ที่อาจเกิดจากหลายคำขอพร้อมกัน
            Article.objects.filter(pk=self.object.pk).update(views=F('views') + 1)
            self.request.session[session_key] = True

        return context
