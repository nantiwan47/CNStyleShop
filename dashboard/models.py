from django.db import models
from accounts.models import UserProfile
from orders.models import OrderItem
from products.models import Product

class Review(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.TextField()
    analysis_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"รีวิว ID: {self.id} โดย {self.user.username}"

class ReviewAnalysis(models.Model):
    POLARITY_CHOICES = [
        ("positive", "คำเชิงบวก"),
        ("negative", "คำเชิงลบ"),
        ("neutral", "เป็นกลาง"),
    ]

    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    score = models.FloatField()
    polarity = models.CharField(max_length=50, choices=POLARITY_CHOICES, default='neutral')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"การวิเคราะห์รีวิว {self.review.id} - ขั้วอารมณ์: {self.polarity}"

# class ReviewPositive(models.Model):
#     analysis = models.ForeignKey(ReviewAnalysis, on_delete=models.CASCADE)
#     positive = models.CharField(max_length=255)
#
# class ReviewNegative(models.Model):
#     analysis = models.ForeignKey(ReviewAnalysis, on_delete=models.CASCADE)
#     negative = models.CharField(max_length=255)

class ReviewSentiment(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'คำเชิงบวก'),
        ('negative', 'คำเชิงลบ'),
    ]

    analysis = models.ForeignKey(ReviewAnalysis, on_delete=models.CASCADE)
    sentiment_type = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    word = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.sentiment_type.capitalize()} Word: {self.word}"