from django import forms
from tinymce.widgets import TinyMCE
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'image']

    # ใช้ TinyMCE widget สำหรับฟิลด์ content
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

