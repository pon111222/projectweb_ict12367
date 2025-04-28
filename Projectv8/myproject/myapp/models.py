from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Menu(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=50, choices=[('staff', 'พนักงาน'), ('manager', 'ผู้จัดการ')])

    def __str__(self):
        return self.user.username

class Order(models.Model):
    SWEETNESS_CHOICES = [
        ('0', 'ไม่หวาน'),
        ('25', 'หวาน 25%'),
        ('50', 'หวาน 50%'),
        ('75', 'หวาน 75%'),
        ('100', 'หวานปกติ'),
    ]

    PEARL_CHOICES = [
        ('none', 'ไม่ใส่ไข่มุก'),
        ('regular', 'ไข่มุกปกติ'),
        ('boba', 'บุก/ไข่มุกใหญ่'),
    ]

    table_number = models.CharField(max_length=10)
    sweetness = models.CharField(max_length=3, choices=SWEETNESS_CHOICES, default='100')
    pearl = models.CharField(max_length=10, choices=PEARL_CHOICES, default='regular')
    created_at = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey(Menu, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    is_delivered = models.BooleanField(default=False)

    def get_total_price(self):
        return self.menu.price * self.quantity if self.menu else 0

    def __str__(self):
        return f"{self.menu} x {self.quantity}"

position = models.CharField(max_length=50, choices=[('staff', 'พนักงาน'), ('manager', 'ผู้จัดการ')])

