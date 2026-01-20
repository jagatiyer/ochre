from django.db import models


class Payment(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField()  # in paise
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} ({self.status})"
