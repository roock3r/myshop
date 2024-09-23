from django.db import models

from orders.models import Order


class Payment(models.Model):
  order = models.OneToOneField(Order, on_delete=models.CASCADE)
  transaction_id = models.CharField(max_length=255, null=True, blank=True)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  payment_url = models.URLField(null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  status = models.CharField(max_length=50, default='Initiated')

  def __str__(self):
    return f"Payment {self.id} for Order {self.order.id}"
