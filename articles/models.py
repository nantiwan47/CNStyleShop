from django.contrib.auth.models import User
from django.db import models
from accounts.models import UserProfile
from tinymce.models import HTMLField

# ฟังก์ชันสำหรับกำหนดเส้นทางการอัปโหลดรูปภาพของบทความ
def upload_to(instance, filename):
    return f"article/{instance.category}/{filename}"

class Article(models.Model):
    CATEGORY_CHOICES = [
        ('lifestyle', 'ไลฟ์สไตล์'),
        ('news', 'ข่าวสาร'),
        ('product recommendatons', 'แนะนำสินค้า'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=255)
    content = HTMLField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to=upload_to)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

