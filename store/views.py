import random
from datetime import datetime

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.mail import send_mail

from .forms import ProductToOrder, OrderPoints, CancelProductInOrder, AddProduct, Search, AddPhoto, AddToStorage, \
    AddToCategory, AddToSubCategory, AddBrand
from .utils import get_all_prods, get_prod_info, get_basket, get_sum_cost, delete_from_order, buy_basket, \
    get_user_orders, cancel_user_order, get_storage_orders, get_products_in_order, get_order_point, \
    get_order, get_email, cancel_order_by_stuff, get_orders_delivery, confirm_delivery, get_order_point_orders, \
    give_order, get_prod_count_in_order, change_prod_in_order, add_product, get_prods_by_id, get_all_prods_main, \
    is_storage_stuff, is_point_stuff, get_categories, get_product_photo_and_id, del_photo, add_on_storage, \
    del_from_storage, del_category, del_sub_category, del_brand
from .models import Product, ProductPhoto, Brand, OrderPoint, OrderStatus, Order, ProductInOrder, ProductOnStorage, \
    Category, SubCategory, StuffCategory
from django.shortcuts import render, redirect


def account(request):
    user = request.user
    return render(request, "basic/account.html",
                  {'user': user})


def index(request):
    user = request.user
    filter_ = request.GET.get('filter')
    prods = get_all_prods_main(filter_)
    categories = get_categories()
    return render(request, "basic/main.html",
                  {'user': user, 'prods': prods, 'data': categories, 'is_storage_stuff': is_storage_stuff(user.id),
                   'is_point_stuff': is_point_stuff(user.id)})


def cansel_order(request):
    user = request.user
    order = request.GET.get('order')
    if cancel_user_order(user.id, order):
        return redirect(f'/product/basket/?msg=Success cansel')
    else:
        return redirect(f'/product/basket/?msg=Something go wrong')


def delete_from_basket(request):
    user = request.user
    order = request.GET.get('order')
    prod_id = request.GET.get('id')
    size = request.GET.get('size')
    if delete_from_order(user.id, order, prod_id, size):
        return redirect(f'/product/basket/?msg=Success delete')
    else:
        return redirect(f'/product/basket/?msg=Something go wrong')


def basket(request):
    user = request.user
    form = OrderPoints()

    if request.method == 'POST':
        order_point_id = request.POST.get('points')
        msg = buy_basket(user.id, order_point_id)
        basket = get_basket(user.id)
        prods = get_all_prods()
        result_sum = get_sum_cost(basket)
        orders = get_user_orders(user.id)
        return render(request, "basic/basket.html",
                      {'form': form, 'orders': orders, 'user': user, 'prods': prods, 'basket': basket,
                       'total': result_sum, 'msg': msg})
    else:
        basket = get_basket(user.id)
        prods = get_all_prods()
        result_sum = get_sum_cost(basket)
        orders = get_user_orders(user.id)
        msg = request.GET.get('msg')
        return render(request, "basic/basket.html",
                      {'form': form, 'orders': orders, 'user': user, 'prods': prods, 'basket': basket,
                       'total': result_sum, 'msg': msg})


def product(request):
    if request.method == 'POST':
        prod_id = request.GET.get("id")
        size = request.POST.get('size')
        count = request.POST.get('count')
        count = int(count)
        user = request.user
        status = OrderStatus.objects.get_or_create(status='Формируется')[0]
        order = Order.objects.filter(is_actual=True, status_id=status.id, user_id=user.id)
        if order.exists():
            print("ok")
        else:
            order_point = OrderPoint.objects.get(id=1)
            date = datetime.now()
            order = [Order.objects.create(is_actual=True, order_point_id=order_point.id,
                                          date=date, user_id=user.id, status_id=status.id)]
        order_id = order[0].id
        pr_in_order = ProductInOrder.objects.filter(order_id=order_id, product_id=prod_id, size=size)
        if pr_in_order.exists():
            product_in_order = pr_in_order[0]
            count_p = product_in_order.count
            count += count_p
            product_in_order.count = count
            product_in_order.save()
        else:
            ProductInOrder.objects.create(order_id=order_id, product_id=prod_id, count=count, size=size)
        return redirect(f'basket/')
    else:
        prod_id = request.GET.get("id")
        prod = get_prod_info(prod_id)
        form = ProductToOrder(prod_id, initial={'count': 1})
        return render(request, "basic/prod_card.html", {'form': form, "prod": prod})


def storage_orders(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        orders = get_storage_orders("Оформлен")
        text = "Ожидают доставки"
        url = "order/?id="
        return render(request, "storage_stuff/storage_orders.html",
                      {'orders': orders[0], 'count': orders[1], 'text': text, 'url': url})
    else:
        return redirect("/")


def storage_canceled_orders(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        orders = get_storage_orders("Отмена")
        text = "Ожидают отмены"
        url = "order/?id="
        return render(request, "storage_stuff/storage_orders.html",
                      {'orders': orders[0], 'count': orders[1], 'text': text, 'url': url})
    else:
        return redirect("/")


def storage_order(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        btn_txt = "Товары переданы в доставку"
        if request.method == 'POST':
            order_id = request.GET.get("id")
            order = get_order(order_id, 'Оформлен')
            if order[0]:
                email_l = get_email(order[1].user_id)
                if email_l[0]:
                    email = email_l[1]
                    send_mail(f'Заказ №{order[1].id}',
                              f'Ваш заказ №{order[1].id} передан в доставку'
                              , 'shop.5tore@yandex.ru',
                              recipient_list=[email], fail_silently=False)
                new_status = OrderStatus.objects.get_or_create(status='В доставке')[0]
                order[1].status_id = new_status.id
                order[1].date = datetime.now()
                order[1].save()
            return redirect('/storage/')
        else:
            user = request.user
            order_id = request.GET.get("id")
            order = get_order(order_id, 'Оформлен')
            if order[0]:
                order = order[1]
                point_id = order.order_point_id
                prods = get_products_in_order(order_id)
                point_l = get_order_point(point_id)
                if point_l[0]:
                    point = point_l[1]
                else:
                    point = []
                return render(request, "storage_stuff/storage_order.html",
                              {'order': order, 'prods': prods, 'point': point, 'btn': btn_txt})
            else:
                msg = "Ошибка, возможно статус заказа изменился"
                return render(request, "storage_stuff/storage_order.html", {'msg': msg, 'btn': btn_txt})
    else:
        return redirect("/")


def storage_canceled_order(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        btn_txt = "Товары приняты на склад"
        if request.method == 'POST':
            order_id = request.GET.get("id")
            order = get_order(order_id, 'Отмена')
            if order[0]:
                if cancel_order_by_stuff(order[1].id):
                    msg = "Заказ отменен и закрыт"
            return redirect(f'/storage/canceled/')
        else:
            user = request.user
            order_id = request.GET.get("id")
            order = get_order(order_id, 'Отмена')
            if order[0]:
                order = order[1]
                if order.is_actual:
                    point_id = order.order_point_id
                    prods = get_products_in_order(order_id)
                    point_l = get_order_point(point_id)
                    if point_l[0]:
                        point = point_l[1]
                    else:
                        point = []
                    return render(request, "storage_stuff/storage_order.html",
                                  {'order': order, 'prods': prods, 'point': point, 'btn': btn_txt})
                else:
                    msg = "Ошибка, возможно статус заказа изменился"
                    return render(request, "storage_stuff/storage_order.html", {'msg': msg, 'btn': btn_txt})
            else:
                msg = "Ошибка, возможно статус заказа изменился"
                return render(request, "storage_stuff/storage_order.html", {'msg': msg, 'btn': btn_txt})
    else:
        return redirect("/")


def order_point_delivery(request):
    user = request.user
    points = []
    if is_point_stuff(user.id) or user.is_superuser:
        if is_point_stuff(user.id):
            order_point_id = StuffCategory.objects.get(user_id=user.id).order_point_id
            order_point = OrderPoint.objects.get(id=order_point_id)
        else:

            points = OrderPoint.objects.all()
            id = request.GET.get("id")
            if id is None:
                id = 1
            order_point = OrderPoint.objects.get(id=id)
            order_point_id = order_point.id
        delivery_list = get_orders_delivery(order_point_id)
        delivery_orders = delivery_list[0]
        count = delivery_list[1]
        text = "Сейчас в доставке"
        url = "delivery_order/?id="
        return render(request, "point_stuff/order_point_delivery.html",
                      {'orders': delivery_orders, 'count': count, 'text': text, 'url': url, 'points': points, "cur_point": order_point})

    else:
        return redirect("/")


def delivery_products(request):
    user = request.user
    if is_point_stuff(user.id) or user.is_superuser:
        btn_txt = "Товары приняты на пункте выдачи"
        if request.method == 'POST':
            order_id = request.GET.get("id")
            order = get_order(order_id, 'В доставке')
            if order[0]:
                if confirm_delivery(order[1].id):
                    msg = "Заказ Принят в пункт выдачи"
                    email_l = get_email(order[1].user_id)
                    if email_l[0]:
                        email = email_l[1]
                        send_mail(f'Заказ №{order[1].id}',
                                  f'Ваш заказ №{order[1].id} доставлен в пункт выдачи и ожидает Вас!'
                                  , 'shop.5tore@yandex.ru',
                                  recipient_list=[email], fail_silently=False)
            return redirect(f'/orderpoint/delivery/')
        else:
            user = request.user
            order_id = request.GET.get("id")
            order = get_order(order_id, 'В доставке')
            if order[0]:
                order = order[1]
                if order.is_actual:
                    prods = get_products_in_order(order_id)

                    return render(request, "point_stuff/storage_order.html",
                                  {'order': order, 'prods': prods, 'btn': btn_txt})
                else:
                    msg = "Ошибка, возможно статус заказа изменился"
                    return render(request, "storage_order.html", {'msg': msg, 'btn': btn_txt})
            else:
                msg = "Ошибка, возможно статус заказа изменился"
                return render(request, "point_stuff/storage_order.html", {'msg': msg, 'btn': btn_txt})

    else:
        return redirect("/")


def order_point_give(request):
    user = request.user
    points = []
    if is_point_stuff(user.id) or user.is_superuser:
        if is_point_stuff(user.id):
            order_point_id = StuffCategory.objects.get(user_id=user.id).order_point_id
            order_point = OrderPoint.objects.get(id=order_point_id)
        else:

            points = OrderPoint.objects.all()
            id = request.GET.get("id")
            if id is None:
                id = 1
            order_point = OrderPoint.objects.get(id=id)
            order_point_id = order_point.id
        orders_list = get_order_point_orders(order_point_id)
        orders = orders_list[0]
        count = orders_list[1]
        text = "Ожидают получения"
        url = "order/?id="
        return render(request, "point_stuff/storage_orders.html",
                      {'orders': orders, 'count': count, 'text': text, 'url': url, 'points': points, "cur_point": order_point})
    else:
        return redirect("/")


def cancel_products(request):
    user = request.user
    if is_point_stuff(user.id) or user.is_superuser:
        btn_txt = "Выдать товары"
        prod_id = request.GET.get("prod")
        order_id = request.GET.get("order")
        size = request.GET.get("size")
        if request.method == 'POST':
            cancel_count = int(request.POST.get('count'))
            if change_prod_in_order(prod_id, order_id, size, cancel_count):
                return redirect(f'/orderpoint/delivered/order/?id={order_id}')
            else:
                msg = "Ошибка, возможно статус заказа изменился"
                return render(request, "point_stuff/give_order.html", {'msg': msg, 'btn': btn_txt})
        else:
            count = get_prod_count_in_order(prod_id, order_id, size)
            if count[0]:
                form = CancelProductInOrder(count[1])

                return render(request, "point_stuff/cancel_form.html", {'form': form})
            else:
                msg = "Ошибка, возможно статус заказа изменился"
                return render(request, "point_stuff/give_order.html", {'msg': msg, 'btn': btn_txt})
    else:
        return redirect("/")


def give_products(request):
    user = request.user
    if is_point_stuff(user.id) or user.is_superuser:
        btn_txt = "Выдать товары"
        if request.method == 'POST':
            order_id = request.GET.get("id")
            order = get_order(order_id, 'Готов к выдаче')
            if order[0]:
                if give_order(order[1].id):
                    msg = "Заказ Принят в пункт выдачи"
                    email_l = get_email(order[1].user_id)
                    if email_l[0]:
                        email = email_l[1]
                        send_mail(f'Заказ №{order[1].id}',
                                  f'Ваш заказ №{order[1].id} выдан. Благодарим за покупку и ждем Вас снова!'
                                  , 'shop.5tore@yandex.ru',
                                  recipient_list=[email], fail_silently=False)
            return redirect(f'/orderpoint/delivered/')
        else:
            order_point = OrderPoint.objects.get(id=1)
            user = request.user
            order_id = request.GET.get("id")
            order = get_order(order_id, 'Готов к выдаче')
            if order[0]:
                order = order[1]
                if order.is_actual:
                    prods = get_products_in_order(order_id)

                    return render(request, "point_stuff/give_order.html",
                                  {'order': order, 'prods': prods, 'point': order_point, 'btn': btn_txt})
                else:
                    msg = "Ошибка, возможно статус заказа изменился"
                    return render(request, "give_order.html", {'msg': msg, 'btn': btn_txt})
            else:
                msg = "Ошибка, возможно статус заказа изменился"

                return render(request, "point_stuff/give_order.html", {'msg': msg, 'btn': btn_txt})
    else:
        return redirect("/")


def add_product_page(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        msg = "Добавьте товар"
        if request.method == 'POST':
            form = AddProduct(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name')
                country = form.cleaned_data.get('country')
                brand_id = form.cleaned_data.get('brand')
                cost = form.cleaned_data.get('cost')
                sex = form.cleaned_data.get('sex')
                sub_category_id = form.cleaned_data.get('sub_category')
                new = add_product(name, country, brand_id, cost, sex, sub_category_id)
                if new[0]:
                    user = request.user
                    prods = get_all_prods()
                    return redirect(f"/storage/product_photos/?id={new[1]}")

        else:
            form = AddProduct()

        return render(request, 'storage_stuff/product_info_red.html', {'form': form, 'msg': msg})
    else:
        return redirect("/")


def change_product(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        msg = ''
        if request.method == 'POST':
            form = AddProduct(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name')
                country = form.cleaned_data.get('country')
                brand_id = form.cleaned_data.get('brand')
                cost = form.cleaned_data.get('cost')
                sex = form.cleaned_data.get('sex')
                category = form.cleaned_data.get('sub_category')
                id = request.GET.get('id')
                try:
                    prod = Product.objects.get(id=id)
                    prod.name = name
                    prod.country = country
                    prod.brand_id = brand_id
                    prod.cost = cost
                    prod.sex = sex
                    prod.sub_category_id = category
                    prod.save()
                    msg = "Изменения сохранены"
                    return redirect(f"/storage/product_photos/?id={id}")
                except ObjectDoesNotExist:
                    msg = "Ошибка, что-то пошло не так"
                except MultipleObjectsReturned:
                    msg = "Ошибка, что-то пошло не так"

        else:
            id = request.GET.get('id')
            form = AddProduct()
            msg = "Редактируйте продукт"
            try:
                prod = Product.objects.get(id=id)
                name = prod.name
                country = prod.country
                brand_id = prod.brand_id
                cost = prod.cost
                sex = prod.sex
                category = prod.sub_category_id
                form = AddProduct(
                    initial={'name': name, 'country': country, 'brand_id': brand_id, 'cost': cost, 'sex': sex,
                             'sub_category': category})
            except ObjectDoesNotExist:
                msg = "Ошибка, что-то пошло не так"
            except MultipleObjectsReturned:
                msg = "Ошибка, что-то пошло не так"

        return render(request, 'storage_stuff/product_info_red.html', {'form': form, 'msg': msg})
    else:
        return redirect("/")


def all_products_page(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        url_s = "/storage/redact_products/on_storage/?id="
        url = "/storage/change_product/?id="
        url_p = "/storage/product_photos/?id="
        if request.method == 'POST':
            form = Search(request.POST)
            if form.is_valid():
                id = form.cleaned_data.get('quest')
                prods = get_prods_by_id(id)
                msg = f"Поиск по id = {id}"
                return render(request, "storage_stuff/products_redaction.html",
                              {'form': form, 'user': user, 'prods': prods, 'msg': msg, 'url': url, 'urls': url_s})
            else:
                prods = get_all_prods()
                msg = f"Ошибка поиска"
                return render(request, "storage_stuff/products_redaction.html",
                              {'form': form, 'user': user, 'prods': prods, 'msg': msg, 'url': url, 'urls': url_s})
        else:
            form = Search()
            prods = get_all_prods()
            msg = f"Все товары"
            return render(request, "storage_stuff/products_redaction.html",
                          {'form': form, 'user': user, 'prods': prods, 'msg': msg, 'url': url, 'url_s': url_s,
                           'url_p': url_p})
    else:
        return redirect("/")


def product_photos(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        text = "Редактируйте фото"
        prod_id = request.GET.get("id")
        photos = get_product_photo_and_id(prod_id)
        if request.method == 'POST':
            form = AddPhoto(request.POST, request.FILES)
            form.save()
            return redirect(f"/storage/product_photos/?id={prod_id}")
        else:
            form = AddPhoto(initial={'product': prod_id})
            return render(request, "storage_stuff/product_photo.html",
                          {'form': form, 'photos': photos, 'id': prod_id, 'text': text})

    else:
        return redirect("/")


def delete_photo(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        photo_id = request.GET.get("id")
        prod_id = request.GET.get("prod_id")
        del_photo(photo_id, prod_id)
        return redirect(f"/storage/product_photos/?id={prod_id}")

    else:
        return redirect("/")


def product_on_storage(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        prod_id = request.GET.get("id")
        size = request.GET.get("size")
        prods = ProductOnStorage.objects.filter(product_id=prod_id)
        if request.method == 'POST':
            form = AddToStorage(request.POST)
            prod = form.save(commit=False)
            product = prod.product_id
            count = prod.count
            size = prod.size
            print(product, count, size)
            add_on_storage(product, count, size)
            return render(request, "storage_stuff/on_storage.html", {'form': form, 'prods': prods, 'id': prod_id})
        else:
            form = AddToStorage(initial={'product': prod_id, 'size': size})
            return render(request, "storage_stuff/on_storage.html", {'form': form, 'prods': prods, 'id': prod_id})
    else:
        return redirect("/")


def delete_prod_on_storage(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        id = request.GET.get("id")
        prod_id = request.GET.get("prod_id")
        del_from_storage(id, prod_id)
        return redirect(f"/storage/redact_products/on_storage/?id={prod_id}")
    else:
        return redirect("/")


def categories_redact(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        cats = Category.objects.all()
        if request.method == 'POST':
            form = AddToCategory(request.POST)
            form.save()
            return redirect("/storage/redact_category/")
        else:
            form = AddToCategory()
            return render(request, "storage_stuff/redact_category.html", {'form': form, 'cats': cats})
    else:
        return redirect("/")


def delete_category(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        id = request.GET.get("id")
        del_category(id)
        return redirect("/storage/redact_category/")
    else:
        return redirect("/")


def sub_category_redact(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        cat_id = request.GET.get("id")
        sub_cats = SubCategory.objects.filter(category_id=cat_id)
        if request.method == 'POST':
            form = AddToSubCategory(request.POST)
            form.save()
            return redirect(f"/storage/redact_category/sub_category_redact/?id={cat_id}")
        else:
            form = AddToSubCategory(initial={'category': cat_id})
            return render(request, "storage_stuff/redact_sub_category.html",
                          {'form': form, 'sub_cats': sub_cats, "cat_id": cat_id})
    else:
        return redirect("/")


def delete_sub_category(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        id = request.GET.get("id")
        cat_id = request.GET.get("cat_id")
        del_sub_category(id, cat_id)
        return redirect(f"/storage/redact_category/sub_category_redact/?id={cat_id}")
    else:
        return redirect("/")


def brand_redact(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        brands = Brand.objects.all()
        if request.method == 'POST':
            form = AddBrand(request.POST)
            form.save()
            return redirect("/storage/redact_brand/")
        else:
            form = AddBrand()
            return render(request, "storage_stuff/redact_brand.html", {'form': form, 'brands': brands})
    else:
        return redirect("/")


def delete_brand(request):
    user = request.user
    if is_storage_stuff(user.id) or user.is_superuser:
        id = request.GET.get("id")
        del_brand(id)
        return redirect("/storage/redact_brand/")
    else:
        return redirect("/")
