from django.urls import path
from myapp import views
from django.urls import path

urlpatterns = [
    # 🔹 หน้าเนื้อหา
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('form/', views.form, name='form'),

    # 🔹 ระบบออเดอร์
    path('order/create/', views.order_create, name='order_create'),
    path('order/<int:order_id>/edit/', views.order_edit, name='order_edit'),
    path('order/<int:order_id>/delete/', views.order_delete, name='order_delete'),
    path('orderitem/<int:item_id>/deliver/', views.mark_item_delivered, name='mark_item_delivered'),

    # 🔹 ระบบตะกร้า
    path('cart/', views.view_cart, name='view_cart'),                           # 🛒 ดูตะกร้า
    path('cart/add/<int:menu_id>/', views.add_to_cart, name='add_to_cart'),      # ➕ เพิ่มเมนูเข้าตะกร้า
    path('cart/remove/<int:menu_id>/', views.remove_from_cart, name='remove_from_cart'),  # ❌ ลบเมนูออกจากตะกร้า
    path('confirm-order/', views.confirm_order, name='confirm_order'),           # ✅ ยืนยันออเดอร์

    # 🔹 ระบบสมาชิก
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 🔹 รายงานยอดขาย / ใบเสร็จ
    path('sales/', views.sales_summary, name='sales_summary'),
    path('receipt/<int:order_id>/', views.receipt_view, name='receipt_view'),
    path('cart/update/<int:menu_id>/', views.update_cart, name='update_cart'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('staff/manage/', views.staff_manage, name='staff_manage'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('staff/reset-password/<int:staff_id>/', views.reset_staff_password, name='reset_staff_password'),
    path('check-new-orders/', views.check_new_orders, name='check_new_orders'),



    path('', views.index, name='home'),

]
