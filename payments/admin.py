from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order_id", "amount", "status", "created_at")
    readonly_fields = ("order_id", "payment_id", "signature", "created_at")
