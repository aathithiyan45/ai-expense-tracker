from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.FloatField()
    category = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"{self.description} - ₹{self.amount} - {self.category}"
