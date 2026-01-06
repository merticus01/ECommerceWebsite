from django.urls import path

from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("products/create/", views.create_product, name="create_product"),
    path("products/<slug:slug>/edit/", views.edit_product, name="edit_product"),
    path("sellers/", views.seller_list, name="seller_list"),
    path("sellers/<slug:slug>/", views.seller_detail, name="seller_detail"),
    path("editorial/", views.editorial_list, name="editorial_list"),
    path("editorial/<slug:slug>/", views.editorial_detail, name="editorial_detail"),
    path("dashboard/seller/", views.seller_dashboard, name="seller_dashboard"),
    path("dashboard/buyer/", views.buyer_dashboard, name="buyer_dashboard"),
    path("cart/", views.view_cart, name="cart"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("search/", views.search, name="search"),
    path("signup/buyer/", views.BuyerSignupView.as_view(), name="register_buyer"),
    path("signup/seller/", views.SellerSignupView.as_view(), name="register_seller"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.logout_user, name="logout"),
]



