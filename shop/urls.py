"""shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.urls import path, include
from store import views
from loggining import views as l_views
from shop import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('register/confirm_email/', l_views.send_m, name='register/mail'),
    path('register/', l_views.reg, name='register'),
    path('product/basket/cansel/', views.cansel_order, name='product/basket/cansel'),
    path('product/basket/delete/', views.delete_from_basket, name='product/basket/delete'),
    path('product/basket/', views.basket, name='product/basket'),
    path('product/', views.product, name='product'),
    path('storage/order/', views.storage_order, name='storage_order'),
    path('storage/canceled/order/', views.storage_canceled_order, name='storage_canceled_order'),
    path('storage/canceled/', views.storage_canceled_orders, name='storage_canceled_orders'),
    path('storage/change_product/', views.change_product, name='change_product'),
    path('storage/add_product/', views.add_product_page, name='add_product'),
    path('storage/redact_products/on_storage/delete/', views.delete_prod_on_storage, name='delete_prod_on_storage'),
    path('storage/redact_products/on_storage/', views.product_on_storage, name='on_storage'),
    path('storage/product_photos/delete/', views.delete_photo, name='delete_photo'),
    path('storage/product_photos/', views.product_photos, name='product_photos'),
    path('storage/redact_products/', views.all_products_page, name='all_product'),
    path('storage/redact_category/delete/', views.delete_category, name='delete_category'),
    path('storage/redact_category/sub_category_redact/delete/', views.delete_sub_category, name='delete_sub_category'),
    path('storage/redact_category/sub_category_redact/', views.sub_category_redact, name='sub_category_redact'),
    path('storage/redact_category/', views.categories_redact, name='categories_redact'),
    path('storage/redact_brand/delete/', views.delete_brand, name='delete_brand'),
    path('storage/redact_brand/', views.brand_redact, name='brand_redact'),
    path('storage/', views.storage_orders, name='storage_orders'),
    path('orderpoint/delivered/order/cancel/', views.cancel_products, name='cancel_product'),
    path('orderpoint/delivered/order/', views.give_products, name='give_order'),
    path('orderpoint/delivery/delivery_order/', views.delivery_products, name='delivery_order_confirm'),
    path('orderpoint/delivered/', views.order_point_give, name='give_point_order'),
    path('orderpoint/delivery/', views.order_point_delivery, name='order_point'),
    path('me_info', views.account, name='account'),
    path('accounts/', include('django.contrib.auth.urls')),
]
# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
