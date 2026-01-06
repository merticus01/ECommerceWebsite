from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.http import HttpResponseForbidden
from .forms import *
from .models import (
    Cart,
    CartItem,
    EditorialArticle,
    Product,
    SellerProfile,
    Era,
    Category,
    Condition,
)

class BuyerSignupView(CreateView):
    model = User 
    form_class = BuyerSignupForm
    template_name = 'marketplace/signup.html'

    def get_context_data(self, **kwargs): # Currently just calls the parent implementation
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/dashboard/buyer/')

class SellerSignupView(CreateView):
    model = User 
    form_class = SellerSignupForm
    template_name = 'marketplace/signup.html'

    def get_context_data(self, **kwargs): # Currently just calls the parent implementation
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        # Create SellerProfile for the user
        SellerProfile.objects.create(
            user=user,
            display_name=user.username,
            slug=user.username.lower()
        )
        login(self.request, user)
        return redirect('/dashboard/seller/')

class UserLoginView(LoginView):
    template_name = 'marketplace/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_seller:
            return '/dashboard/seller/' 
        elif user.is_buyer:
            return '/dashboard/buyer/'
        else:
            return '/'

def logout_user(request):
    logout(request) # logs out the user and redirects to homepage
    return redirect('/')

def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def homepage(request):
    featured_products = (
        Product.objects.filter(is_featured=True, is_active=True)
        .select_related("seller")
        .prefetch_related("images")[:8]
    )
    new_arrivals = (
        Product.objects.filter(is_active=True)
        .order_by("-created_at")
        .select_related("seller")
        .prefetch_related("images")[:12]
    )
    editorial_features = EditorialArticle.objects.filter(published=True)[:3]

    context = {
        "featured_products": featured_products,
        "new_arrivals": new_arrivals,
        "editorial_features": editorial_features,
    }
    return render(request, "marketplace/homepage.html", context)


def product_list(request):
    products = Product.objects.filter(is_active=True)

    era = request.GET.get("era")
    category = request.GET.get("category")
    condition = request.GET.get("condition")
    location = request.GET.get("location")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    search_query = request.GET.get("q")

    if era:
        products = products.filter(era=era)
    if category:
        products = products.filter(category=category)
    if condition:
        products = products.filter(condition=condition)
    if location:
        products = products.filter(seller__location__icontains=location)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(story__icontains=search_query)
        )

    # Order and optimize query: include seller and images to avoid per-item queries in templates
    products = products.order_by("-created_at").select_related("seller").prefetch_related("images")

    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 24)  # 24 items per page
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    context = {
        "products": products_page,
        "paginator": paginator,
        "product_era_choices": Era.choices,
        "product_category_choices": Category.choices,
        "product_condition_choices": Condition.choices,
    }
    return render(request, "marketplace/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("seller").prefetch_related("images"),
        slug=slug,
        is_active=True,
    )
    cart = _get_or_create_cart(request)
    in_cart = cart.items.filter(product=product).exists()

    context = {
        "product": product,
        "in_cart": in_cart,
    }
    return render(request, "marketplace/product_detail.html", context)

@login_required
def seller_list(request):
    sellers = SellerProfile.objects.filter(verified=True)
    context = {"sellers": sellers}
    return render(request, "marketplace/seller_list.html", context)

@login_required
def seller_detail(request, slug):
    seller = get_object_or_404(SellerProfile, slug=slug, verified=True)
    products = seller.products.filter(is_active=True)
    context = {
        "seller": seller,
        "products": products,
    }
    return render(request, "marketplace/seller_detail.html", context)


def editorial_list(request):
    articles = EditorialArticle.objects.filter(published=True)
    context = {"articles": articles}
    return render(request, "marketplace/editorial_list.html", context)


def editorial_detail(request, slug):
    article = get_object_or_404(EditorialArticle, slug=slug, published=True)
    context = {"article": article}
    return render(request, "marketplace/editorial_detail.html", context)


@login_required
def seller_dashboard(request):
    if not request.user.is_seller:
        return HttpResponseForbidden("Only sellers can access this page.")
    
    seller = getattr(request.user, "seller_profile", None)
    products = []
    if request.user.is_seller:
        products = seller.products.all()
    context = {"seller": seller, "products": products}
    return render(request, "marketplace/seller_dashboard.html", context)


@login_required
def create_product(request):
    if not request.user.is_seller:
        return HttpResponseForbidden("Only sellers can create products.")
    
    seller = request.user.seller_profile
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    
    context = {'form': form}
    return render(request, 'marketplace/create_product.html', context)


@login_required
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    # Check if user is the seller
    if product.seller.user != request.user:
        return HttpResponseForbidden("You can only edit your own products.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'product': product}
    return render(request, 'marketplace/edit_product.html', context)


@login_required
def buyer_dashboard(request):
    orders = request.user.orders.all()
    favorites = request.user.favorites.select_related("product")
    context = {"orders": orders, "favorites": favorites}
    return render(request, "marketplace/buyer_dashboard.html", context)

@login_required
def view_cart(request):
    cart = _get_or_create_cart(request)
    context = {"cart": cart}
    return render(request, "marketplace/cart.html", context)

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = _get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return redirect("cart")


@login_required
def checkout(request):
    cart = _get_or_create_cart(request)
    if request.method == "POST":
        # Create an Order
        order = Order.objects.create(
            buyer=request.user,
            total=cart.total,
            status=Order.Status.PENDING
        )
        
        # Create OrderItems from CartItems
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                seller=item.product.seller,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # Clear the cart
        cart.items.all().delete()
        
        return redirect('buyer_dashboard')

    context = {"cart": cart}
    return render(request, "marketplace/checkout.html", context)


def search(request):
    return product_list(request)


