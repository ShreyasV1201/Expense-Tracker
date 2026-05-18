# expenseTracker/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

class Expense(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    date        = models.DateField()
    category    = models.CharField(max_length=100)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} – {self.category} – {self.amount}"
    
class Income(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    date        = models.DateField()
    category    = models.CharField(max_length=100)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

class Profile(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)
    mobile     = models.CharField(max_length=20,    blank=True)
    address    = models.CharField(max_length=255,   blank=True)

    def __str__(self):
        return f"{self.user.username}’s profile"
    
class Recurring_expenses(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True
    )

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
    )

    def __str__(self):
        return f"{self.amount} - {self.frequency} - {self.status}"
