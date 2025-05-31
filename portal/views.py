from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ProductForm
from .models import Product, CartItem, Order, OrderItem


@login_required(login_url='login')
def home(request):
    products = Product.objects.all()[:4]  # get first 4 products for featured
    return render(request, 'home.html', {'products': products})


@login_required(login_url='login')
def about(request):
    return render(request, 'about.html')


@login_required(login_url='login')
def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


def user_login(request):
    if request.method == 'POST':
        uname = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(request, username=uname, password=pwd)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')


def user_register(request):
    if request.method == 'POST':
        uname = request.POST['username']
        email = request.POST['email']
        pwd = request.POST['password']
        cpwd = request.POST['confirm_password']

        if pwd != cpwd:
            messages.error(request, 'Passwords do not match!')
        elif User.objects.filter(username=uname).exists():
            messages.error(request, 'Username already exists!')
        else:
            user = User.objects.create_user(
                username=uname, email=email, password=pwd)
            user.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    return render(request, 'register.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


# views.py
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    cart_item = CartItem.objects.filter(
        product=product, user=request.user).first()
    current_quantity = cart_item.quantity if cart_item else 1

    return render(request, 'product_detail.html', {
        'product': product,
        'current_quantity': current_quantity
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    requested_quantity = int(request.POST.get('quantity', 1))

    if requested_quantity < 1:
        requested_quantity = 1

    cart = request.session.get('cart', {})
    current_in_cart = cart.get(str(product_id), 0)

    remaining_stock = product.stock - current_in_cart

    if remaining_stock <= 0:
        messages.error(
            request, f"{product.name} already in cart with max available stock!")
        return redirect('product_detail', id=product.id)

    # Limit to remaining stock
    final_quantity_to_add = min(requested_quantity, remaining_stock)
    cart[str(product_id)] = current_in_cart + final_quantity_to_add
    request.session['cart'] = cart

    if final_quantity_to_add < requested_quantity:
        messages.warning(
            request, f"Only {final_quantity_to_add} more of {product.name} added. Stock limit reached."
        )
    else:
        messages.success(
            request, f"{product.name} added to cart (Quantity: {final_quantity_to_add})!")

    return redirect('product_detail', id=product.id)


@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': item_total  # match your template variable
            })
            total_price += item_total
        except Product.DoesNotExist:
            continue

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def checkout_view(request):
    return render(request, 'checkout.html')


# @require_POST
# def process_checkout(request):
#     first_name = request.POST.get('first_name')
#     last_name = request.POST.get('last_name')
#     address = request.POST.get('address')
#     city = request.POST.get('city')
#     zip_code = request.POST.get('zip_code')

#     # Create order
#     order = Order.objects.create(
#         customer=request.user,
#         first_name=first_name,
#         last_name=last_name,
#         address=address,
#         city=city,
#         zip_code=zip_code
#     )

#     # Save cart items as OrderItems
#     cart = request.session.get('cart', {})
#     for product_id, quantity in cart.items():
#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             continue  # skip invalid products

#         OrderItem.objects.create(
#             order=order,
#             product=product,
#             price=product.price,
#             quantity=quantity
#         )

#     # Clear cart
#     if 'cart' in request.session:
#         del request.session['cart']
#     request.session.modified = True

#     return render(request, 'greatful.html', {'name': first_name, 'order': order})


@require_POST
def process_checkout(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    address = request.POST.get('address')
    city = request.POST.get('city')
    zip_code = request.POST.get('zip_code')

    order = Order.objects.create(
        customer=request.user,
        first_name=first_name,
        last_name=last_name,
        address=address,
        city=city,
        zip_code=zip_code
    )

    cart = request.session.get('cart', {})
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)

            OrderItem.objects.create(
                order=order,
                product_name=product.name,
                price=product.price,
                quantity=quantity
            )

            if product.stock >= quantity:
                product.stock -= quantity
                product.save()
            else:
                messages.warning(
                    request, f"Not enough stock for {product.name}. Ordered: {quantity}, Available: {product.stock}")

        except Product.DoesNotExist:
            continue

    request.session.pop('cart', None)
    request.session.modified = True

    return render(request, 'greatful.html', {'name': first_name, 'order': order})


@login_required
@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
@staff_member_required
def delete_products(request):
    products = Product.objects.all()
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('delete_products')
    return render(request, 'delete_product.html', {'products': products})


@login_required
def order_list(request):
    if request.user.is_staff:
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(
            customer=request.user).order_by('-created_at')

    return render(request, 'order_list.html', {'orders': orders})


# views.py


# @login_required
# def update_cart_quantity(request, product_id):
#     if request.method == 'POST':
#         action = request.POST.get('action')  # 'increase' or 'decrease'

#         cart = request.session.get('cart', {})

#         current_qty = cart.get(str(product_id), 1)

#         if action == 'increase':
#             current_qty += 1
#             cart[str(product_id)] = current_qty
#         elif action == 'decrease':
#             if current_qty > 1:
#                 current_qty -= 1
#                 cart[str(product_id)] = current_qty
#             else:
#                 cart.pop(str(product_id), None)

#         request.session['cart'] = cart
#         request.session.modified = True

#     return redirect('product_detail', id=product_id)


# @login_required
# def update_cart_quantity(request, product_id):
#     if request.method == 'POST':
#         try:
#             product = get_object_or_404(Product, id=product_id)
#             action = request.POST.get('action', '').lower()
#             cart = request.session.get('cart', {})
#             product_key = str(product_id)

#             current_qty = cart.get(product_key, 1)

#             if action == 'increase':
#                 # Ensure we don't exceed available stock
#                 if current_qty < product.stock:
#                     current_qty += 1
#                     cart[product_key] = current_qty
#                     messages.success(
#                         request, f"Quantity increased for {product.name}")
#                 else:
#                     messages.warning(
#                         request, f"Cannot exceed available stock ({product.stock})")
#             elif action == 'decrease':
#                 if current_qty > 1:
#                     current_qty -= 1
#                     cart[product_key] = current_qty
#                     messages.success(
#                         request, f"Quantity decreased for {product.name}")
#                 else:
#                     # Remove item if quantity would go to 0
#                     cart.pop(product_key, None)
#                     messages.info(request, f"{product.name} removed from cart")
#             else:
#                 messages.error(request, "Invalid action requested")

#             request.session['cart'] = cart
#             request.session.modified = True

#         except Exception as e:
#             messages.error(
#                 request, "An error occurred while updating your cart")
#             # Log the error for debugging
#             print(f"Error updating cart: {str(e)}")

#     # Redirect back to either the product detail or cart page based on referrer
#     referer = request.META.get('HTTP_REFERER')
#     if referer and 'cart' in referer:
#         return redirect('cart')
#     return redirect('product_detail', id=product_id)


@login_required
def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            action = request.POST.get('action')

            cart = request.session.get('cart', {})
            product_key = str(product_id)
            current_qty = cart.get(product_key, 1)

            if action == 'increase':
                current_qty += 1
            elif action == 'decrease':
                current_qty = max(1, current_qty - 1)  # Never go below 1

            cart[product_key] = current_qty
            request.session['cart'] = cart
            request.session.modified = True

            # Update database cart if using database
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': current_qty}
            )
            if not created:
                cart_item.quantity = current_qty
                cart_item.save()

        except Exception as e:
            messages.error(request, "Couldn't update quantity")
            print(f"Error: {e}")

    return redirect('product_detail', id=product_id)


@login_required
@staff_member_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


# views.py
# from django.shortcuts import redirect, get_object_or_404
# from .models import Product, CartItem  # adjust as needed

# def update_cart_quantity(request, id):
#     if request.method == "POST":
#         product = get_object_or_404(Product, id=id)
#         quantity = int(request.POST.get("quantity", 1))

#         # Get cart item
#         cart_item = CartItem.objects.filter(product=product, user=request.user).first()
#         if cart_item:
#             cart_item.quantity = quantity
#             cart_item.save()
#         else:
#             # Optional: Create if not found
#             CartItem.objects.create(product=product, user=request.user, quantity=quantity)

#         return redirect('product_detail', id=id)
