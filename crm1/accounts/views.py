from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect

from .filters import OrderFilter
from .forms import OrderForm, CreateUserForm
from .models import *


# Create your views here.

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, 'account was created for ' + username)
                return redirect('login')

        context = {'form': form}
        return render(request, 'accounts/register.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'username or password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)


def logOutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login/')
def home(request):
    Orders = Order.objects.all()
    total_orders = Orders.count()
    orders_delivered = Order.objects.filter(status='Delivered').count()
    orders_pending = Order.objects.filter(status='Pending').count()
    Customers = Customer.objects.all()
    Products = Product.objects.all()
    context = {'Orders': Orders, 'Customers': Customers, 'Products': Products, 'total_orders': total_orders,
               'orders_delivered': orders_delivered, 'orders_pending': orders_pending}

    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def products(request):
    products = Product.objects.all()

    return render(request, 'accounts/products.html', {"products": products})


@login_required(login_url='login')
def customer(request, pk_test):
    Customers = Customer.objects.get(id=pk_test)
    customer_orders = Customers.order_set.all()
    total_orders = Customers.order_set.all().count()

    myFilter = OrderFilter(request.GET, queryset=customer_orders)
    customer_orders = myFilter.qs

    context = {'customer_orders': customer_orders, 'Customers': Customers, 'total_orders': total_orders,
               'myFilter': myFilter}
    return render(request, 'accounts/customers.html', context)


@login_required(login_url='login')
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
    customers = Customer.objects.get(id=pk)
    # form=OrderForm(initial={'customer':customers})
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customers)
    if request.method == 'POST':
        # print('printing post',request.POST)
        formset = OrderFormSet(request.POST, instance=customers)
        # form=OrderForm(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'formset': formset}
    return render(request, 'accounts/orders_form.html', context)


@login_required(login_url='login')
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        # print('printing post',request.POST)
        form = OrderForm(request.POST,
                         instance=order)  # instance would update in same order, otherwise a new feold is created
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'accounts/orders_form.html', context)


@login_required(login_url='login')
def deleteOrder(request, pk1):
    order = Order.objects.get(id=pk1)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {'item': order}
    return render(request, 'accounts/delete.html', context)
