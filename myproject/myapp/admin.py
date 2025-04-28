
from django.contrib import admin
from .models import Category, Menu, Employee, Order, OrderItem

admin.site.register(Category)
admin.site.register(Menu)
admin.site.register(Employee)
admin.site.register(Order)
admin.site.register(OrderItem)
