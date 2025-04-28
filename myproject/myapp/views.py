from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import F
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Menu, Order, OrderItem, Employee, Category


# 🔐 หน้าแรก
from django.db.models import Q

def index(request):
    search_query = request.GET.get('search', '')

    if search_query:
        if search_query.isdigit():
            # ถ้า search เป็นตัวเลข ➔ หา Order ID ตรง ๆ
            orders = Order.objects.filter(id=int(search_query)).order_by('-id')
        else:
            # ถ้าเป็นข้อความ ➔ หาเมนูที่ตรงกับข้อความ
            orders = Order.objects.filter(menu_name__icontains=search_query).order_by('-id')
    else:
        # ไม่ได้ค้นหา ➔ แสดงทั้งหมด
        orders = Order.objects.all().order_by('-id')

    return render(request, "index.html", {"orders": orders, "search": search_query})


def about(request):
    return render(request, "about.html")

def contact(request):
    return HttpResponse("<h1>ติดต่อเราได้ที่เบอร์ ... </h1>")

def form(request):
    employees = Employee.objects.all()
    return render(request, "form.html", {"employees": employees})

# ✅ สร้างออเดอร์
@login_required(login_url="login")
def order_create(request):
    employees = Employee.objects.all()
    if request.method == "POST":
        table_number = request.POST.get("table_number")
        sweetness = request.POST.get("sweetness")
        pearl = request.POST.get("pearl")
        employee_id = request.POST.get("employee_id")

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return HttpResponse("ไม่พบพนักงาน", status=404)

        order = Order.objects.create(
            table_number=table_number,
            sweetness=sweetness,
            pearl=pearl,
            employee=employee
        )

        # เพิ่มเมนูแรกเป็นตัวอย่าง
        menu = Menu.objects.first()
        if menu:
            OrderItem.objects.create(
                order=order,
                menu=menu,
                quantity=1,
                comment="ไม่มีน้ำแข็ง"
            )

        return redirect("index")

    return render(request, "order_form.html", {"employees": employees})

# ✅ แก้ไขออเดอร์
@login_required(login_url="login")
def order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    employees = Employee.objects.all()

    if request.method == "POST":
        order.table_number = request.POST.get("table_number")
        order.sweetness = request.POST.get("sweetness")
        order.pearl = request.POST.get("pearl")
        employee_id = request.POST.get("employee_id")

        try:
            employee = Employee.objects.get(id=employee_id)
            order.employee = employee
        except Employee.DoesNotExist:
            return HttpResponse("พนักงานไม่ถูกต้อง", status=404)

        order.save()
        return redirect("index")

    return render(request, "order_edit_form.html", {
        "order": order,
        "employees": employees
    })

# ✅ ลบออเดอร์
@login_required(login_url="login")
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect("index")

# ✅ ล็อกอิน
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "login.html", {"error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"})
    return render(request, "login.html")

# ✅ ล็อกเอาท์
def logout_view(request):
    logout(request)
    return redirect("login")

# ✅ รายงานยอดขาย
@login_required(login_url="login")
def sales_summary(request):
    employee = Employee.objects.filter(user=request.user).first()

    # ถ้าไม่ใช่ Manager, ไม่ให้ดู
    if not employee or employee.position != 'manager':
        return redirect('index')  # หรือจะแสดง error ก็ได้

    today = now().date()
    today_sales = OrderItem.objects.filter(order__created_at__date=today)
    total_today = sum(item.get_total_price() for item in today_sales)

    all_orders = Order.objects.all()
    all_total = sum(
        item.get_total_price()
        for order in all_orders
        for item in order.items.all()
    )

    return render(request, "sales_summary.html", {
        "today_sales": today_sales,
        "total_today": total_today,
        "all_total": all_total,
    })



# ✅ ปุ่มจัดส่งแล้ว
@require_POST
@login_required(login_url="login")
def mark_item_delivered(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    item.is_delivered = True
    item.save()
    return redirect("index")

# ✅ ใบเสร็จ
@login_required(login_url="login")
def receipt_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    total = sum(item.get_total_price() for item in items)

    return render(request, "receipt.html", {
        "order": order,
        "items": items,
        "total": total
    })
@login_required(login_url="login")
def index(request):
    search_query = request.GET.get("search", "")
    
    if search_query:
        orders = Order.objects.filter(
            items__menu__name__icontains=search_query
        ).distinct().order_by('-created_at')[:10]
    else:
        orders = Order.objects.all().order_by('-created_at')[:10]
        
    menus = Menu.objects.all()

    return render(request, "index.html", {
        "menus": menus,
        "orders": orders,
        "search": search_query,
    })

menus = Menu.objects.all()


@login_required(login_url="login")
def order_create(request):
    menus = Menu.objects.all()
    return render(request, "order_create.html", {"menus": menus})

@require_POST
@login_required(login_url="login")
def add_to_cart(request, menu_id):
    cart = request.session.get('cart', {})
    cart[menu_id] = cart.get(menu_id, 0) + 1
    request.session['cart'] = cart
    return redirect('order_create')

@login_required(login_url="login")
def view_cart(request):
    cart = request.session.get('cart', {})
    menus = Menu.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for menu in menus:
        quantity = cart.get(str(menu.id), 0)
        item_total = menu.price * quantity
        total += item_total
        cart_items.append({
            'menu': menu,
            'quantity': quantity,
            'item_total': item_total,
        })

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
    })

@require_POST
@login_required(login_url="login")
def confirm_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('view_cart')  # ถ้าตะกร้าว่างกลับไปที่ตะกร้า

    employee = Employee.objects.filter(user=request.user).first()
    if not employee:
        return HttpResponse("ไม่พบข้อมูลพนักงาน", status=404)

    # สร้างออเดอร์ใหม่
    order = Order.objects.create(
        table_number="-",  # ยังไม่ใช้โต๊ะเลยใส่ขีด
        sweetness='100',
        pearl='regular',
        employee=employee
    )

    # สร้าง OrderItem จากตะกร้า
    for menu_id, quantity in cart.items():
        menu = get_object_or_404(Menu, id=menu_id)
        OrderItem.objects.create(
            order=order,
            menu=menu,
            quantity=quantity,
            comment=""
        )

    # ล้างตะกร้า
    request.session['cart'] = {}

    return redirect('index')

@require_POST
@login_required(login_url="login")
def add_to_cart(request, menu_id):
    cart = request.session.get('cart', {})

    sweetness = request.POST.get('sweetness', '100')
    pearl = request.POST.get('pearl', 'regular')

    cart[menu_id] = {
        'quantity': cart.get(menu_id, {}).get('quantity', 0) + 1,
        'sweetness': sweetness,
        'pearl': pearl,
    }
    request.session['cart'] = cart

    return redirect('order_create')

@login_required(login_url="login")
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for menu_id, item in cart.items():
        try:
            menu = Menu.objects.get(id=menu_id)
            total = menu.price * item['quantity']
            total_price += total

            cart_items.append({
                'menu': menu,
                'quantity': item['quantity'],
                'sweetness': item.get('sweetness', '100'),
                'pearl': item.get('pearl', 'regular'),
                'total_price': total,
                'get_sweetness_display': lambda: sweetness_display(item.get('sweetness', '100')),
                'get_pearl_display': lambda: pearl_display(item.get('pearl', 'regular')),
            })
        except Menu.DoesNotExist:
            continue

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_price": total_price,
    })

# ===== ใส่บนสุดของ views.py =====

def sweetness_display(value):
    choices = {
        '0': 'ไม่หวาน',
        '25': 'หวาน 25%',
        '50': 'หวาน 50%',
        '75': 'หวาน 75%',
        '100': 'หวานปกติ',
    }
    return choices.get(str(value), 'ไม่ระบุ')

def pearl_display(value):
    choices = {
        'none': 'ไม่ใส่ไข่มุก',
        'regular': 'ไข่มุกปกติ',
        'boba': 'บุก/ไข่มุกใหญ่',
    }
    return choices.get(str(value), 'ไม่ระบุ')

from django.shortcuts import redirect

from django.views.decorators.http import require_POST
from django.shortcuts import redirect

@require_POST
@login_required(login_url="login")
def remove_from_cart(request, menu_id):
    cart = request.session.get('cart', {})
    menu_id_str = str(menu_id)  # ต้องแปลงเป็น string เพราะ key ใน session เป็น string

    if menu_id_str in cart:
        del cart[menu_id_str]  # ลบเมนูออกจากตะกร้า

    request.session['cart'] = cart
    return redirect('view_cart')


from django.shortcuts import redirect

@require_POST
def confirm_order(request):
    cart = request.session.get('cart', [])
    employee_id = request.user.employee.id if hasattr(request.user, 'employee') else None

    if not cart or not employee_id:
        return redirect('order_create')  # หรือหน้าอื่นถ้าไม่มีข้อมูล

    order = Order.objects.create(
        sweetness=cart[0]['sweetness'],
        pearl=cart[0]['pearl'],
        employee_id=employee_id,
    )

    for item in cart:
        menu = get_object_or_404(Menu, id=item['menu_id'])
        OrderItem.objects.create(
            order=order,
            menu=menu,
            quantity=item['quantity'],
            comment=item.get('comment', '')
        )

@require_POST
@login_required(login_url="login")
def confirm_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('view_cart')

    employee = Employee.objects.filter(user=request.user).first()
    if not employee:
        return HttpResponse("ไม่พบข้อมูลพนักงาน", status=404)

    # สร้างออเดอร์ใหม่
    order = Order.objects.create(
        table_number="-",
        sweetness=list(cart.values())[0].get('sweetness', '100'),
        pearl=list(cart.values())[0].get('pearl', 'regular'),
        employee=employee
    )

    for menu_id, item in cart.items():
        menu = get_object_or_404(Menu, id=menu_id)
        OrderItem.objects.create(
            order=order,
            menu=menu,
            quantity=item.get('quantity', 1),
            comment=item.get('comment', '')
        )

    request.session['cart'] = {}  # ✅ เคลียร์ตะกร้า
    return redirect('index')      # ✅ กลับหน้าแรก

from django.views.decorators.http import require_POST

@require_POST
@login_required(login_url="login")
def add_to_cart(request, menu_id):
    cart = request.session.get('cart', {})

    sweetness = request.POST.get('sweetness', '100')
    pearl = request.POST.get('pearl', 'regular')
    quantity = int(request.POST.get('quantity', 1))  # รับจำนวนแก้วที่เลือก

    if menu_id not in cart:
        cart[menu_id] = {
            'quantity': 0,
            'sweetness': sweetness,
            'pearl': pearl,
        }

    cart[menu_id]['quantity'] += quantity  # บวกจำนวนแก้วที่เลือก
    request.session['cart'] = cart

    return redirect('order_create')


@require_POST
@login_required(login_url="login")
def update_cart(request, menu_id):
    cart = request.session.get('cart', {})

    action = request.POST.get('action')

    if str(menu_id) in cart:
        if action == 'increase':
            cart[str(menu_id)]['quantity'] += 1
        elif action == 'decrease':
            cart[str(menu_id)]['quantity'] -= 1
            if cart[str(menu_id)]['quantity'] <= 0:
                del cart[str(menu_id)]

        request.session['cart'] = cart

    return redirect('view_cart')

from django.db.models import Sum, Count
from django.utils import timezone

@login_required(login_url="login")
def dashboard(request):
    today = timezone.now().date()

    # ยอดขายวันนี้
    today_sales = OrderItem.objects.filter(order__created_at__date=today)
    total_today = sum(item.get_total_price() for item in today_sales)

    # ยอดขายรวมทั้งหมด
    all_sales = OrderItem.objects.all()
    total_all = sum(item.get_total_price() for item in all_sales)

    # สรุปยอดขาย 7 วันล่าสุด
    from datetime import timedelta
    sales_by_day = []
    for i in range(7):
        day = today - timedelta(days=i)
        daily_total = OrderItem.objects.filter(order__created_at__date=day)
        daily_sum = sum(item.get_total_price() for item in daily_total)
        sales_by_day.append({
            'date': day.strftime('%d/%m'),
            'total': daily_sum
        })
    sales_by_day.reverse()  # เรียงวันเก่าสุด > ใหม่สุด

    # ห้าเมนูขายดีที่สุด
    top_menus = (OrderItem.objects
                 .values('menu__name')
                 .annotate(total_quantity=Sum('quantity'))
                 .order_by('-total_quantity')[:5])

    return render(request, "dashboard.html", {
        'total_today': total_today,
        'total_all': total_all,
        'sales_by_day': sales_by_day,
        'top_menus': top_menus,
    })

from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

@login_required(login_url="login")
def sales_summary(request):
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()

    today_sales = OrderItem.objects.filter(order__created_at__date=selected_date)
    total_today = sum(item.get_total_price() for item in today_sales)

    all_orders = OrderItem.objects.all()
    all_total = sum(item.get_total_price() for item in all_orders)

    # รายงานยอดขายรายวัน 7 วันล่าสุด
    sales_by_day = []
    for i in range(6, -1, -1):  # 6 วันก่อน -> วันนี้
        day = timezone.now().date() - timedelta(days=i)
        day_sales = OrderItem.objects.filter(order__created_at__date=day)
        total = sum(item.get_total_price() for item in day_sales)
        sales_by_day.append({'day': day.strftime('%d/%m'), 'total': total})

    # รายงานยอดขายรายเดือน
    from django.db.models.functions import TruncMonth
    monthly_sales = (OrderItem.objects
        .annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(total=Sum(F('menu__price') * F('quantity')))
        .order_by('month')
    )

    # Top 5 เมนูขายดีที่สุด
    top_menus = (OrderItem.objects
        .values('menu__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )

    return render(request, "sales_summary.html", {
        'today_sales': today_sales,
        'total_today': total_today,
        'all_total': all_total,
        'selected_date': selected_date,
        'daily_sales': sales_by_day,
        'monthly_sales': monthly_sales,
        'top_menus': top_menus,
    })

from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth

@login_required(login_url="login")
def sales_summary(request):
    employee = Employee.objects.filter(user=request.user).first()

    # 🔒 จำกัดเฉพาะ Manager เท่านั้น
    if not employee or employee.position != 'manager':
        return redirect('index')

    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()

    # 🔹 ยอดขายของวันที่เลือก
    today_sales = OrderItem.objects.filter(order__created_at__date=selected_date)
    total_today = sum(item.get_total_price() for item in today_sales)

    # 🔹 ยอดขายรวมทั้งหมด
    all_orders = OrderItem.objects.all()
    all_total = sum(item.get_total_price() for item in all_orders)

    # 🔹 กราฟยอดขาย 7 วันล่าสุด
    sales_by_day = []
    for i in range(6, -1, -1):  # 6 วันก่อน -> วันนี้
        day = timezone.now().date() - timedelta(days=i)
        day_sales = OrderItem.objects.filter(order__created_at__date=day)
        total = sum(item.get_total_price() for item in day_sales)
        sales_by_day.append({'day': day.strftime('%d/%m'), 'total': total})

    # 🔹 ยอดขายรวมตามเดือน
    monthly_sales = (
        OrderItem.objects
        .annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(total=Sum(F('menu__price') * F('quantity')))
        .order_by('month')
    )

    # 🔹 Top 5 เมนูขายดีที่สุด
    top_menus = (
        OrderItem.objects
        .values('menu__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )

    return render(request, "sales_summary.html", {
        'today_sales': today_sales,
        'total_today': total_today,
        'all_total': all_total,
        'selected_date': selected_date,
        'daily_sales': sales_by_day,
        'monthly_sales': monthly_sales,
        'top_menus': top_menus,
    })


@login_required(login_url="login")
def order_create(request):
    category_id = request.GET.get('category')  # รับ id หมวดหมู่จาก URL

    if category_id:
        menus = Menu.objects.filter(category_id=category_id)
    else:
        menus = Menu.objects.all()

    categories = Category.objects.all()  # ดึงหมวดหมู่ทั้งหมดมาโชว์

    return render(request, "order_create.html", {
        "menus": menus,
        "categories": categories,
        "selected_category": category_id,
    })


from django.contrib.auth.models import User

@login_required(login_url="login")
def staff_manage(request):
    employee = Employee.objects.filter(user=request.user).first()

    # เช็กเฉพาะ Manager เข้าได้
    if not employee or employee.position != 'manager':
        return redirect('index')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # สร้าง User ใหม่
        user = User.objects.create_user(username=username, password=password)

        # สร้าง Employee ให้ User นั้น (ตำแหน่ง: staff)
        Employee.objects.create(user=user, position='staff')

        return redirect('staff_manage')

    staff_list = Employee.objects.filter(position='staff')
    return render(request, 'staff_manage.html', {
        'staff_list': staff_list,
    })

@require_POST
@login_required(login_url="login")
def delete_staff(request, staff_id):
    employee = Employee.objects.filter(id=staff_id, position='staff').first()

    if employee:
        employee.user.delete()  # ลบ User ด้วย
        employee.delete()

    return redirect('staff_manage')


@require_POST
@login_required(login_url="login")
def reset_staff_password(request, staff_id):
    employee = Employee.objects.filter(id=staff_id, position='staff').first()

    if employee:
        new_password = request.POST.get('new_password')
        user = employee.user
        user.set_password(new_password)
        user.save()

    return redirect('staff_manage')

from django.http import JsonResponse
from .models import Order
from django.utils.timezone import now

def check_new_orders(request):
    last_check = request.session.get('last_check', None)
    if last_check:
        new_orders = Order.objects.filter(created_at__gt=last_check).exists()
    else:
        new_orders = False

    request.session['last_check'] = now().isoformat()
    return JsonResponse({'new_order': new_orders})

from django.http import JsonResponse
from .models import Order
from django.utils.timezone import now

def check_new_orders(request):
    last_check = request.session.get('last_check', None)
    if last_check:
        new_orders = Order.objects.filter(created_at__gt=last_check).exists()
    else:
        new_orders = False

    request.session['last_check'] = now().isoformat()
    return JsonResponse({'new_order': new_orders})

from django.http import JsonResponse
from .models import Order

