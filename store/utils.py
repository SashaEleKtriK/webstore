import json
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import User

from .models import Product, ProductPhoto, Brand, ProductOnStorage, Order, OrderStatus, ProductInOrder, OrderPoint, \
    StuffCategory, Category, SubCategory


def get_prod_by_id(id):
    product = Product.objects.get(id=id)
    return product


def get_order_status(order_id):
    order = Order.objects.get(id=order_id)
    status = OrderStatus.objects.get(id=order.status_id).status
    return status


def get_email(user_id):
    result = []
    try:
        user = User.objects.get(id=user_id)
        result.append(True)
        result.append(user.email)
    except ObjectDoesNotExist:
        result.append(False)
    except MultipleObjectsReturned:
        result.append(False)
    return result


def get_prod_on_storage(prod_id):
    product_storage = ProductOnStorage.objects.raw(
        f"SELECT id, size, count, product_id FROM store_productonstorage WHERE count > 0 AND product_id = {prod_id}")
    return product_storage


def cancel_user_order(user_id, order_id):
    orders = Order.objects.filter(id=order_id, user_id=user_id)
    if orders.exists():
        order = orders[0]
        if order.is_actual:
            new_status = OrderStatus.objects.get_or_create(status='Отмена')[0]
            order.status_id = new_status.id
            order.save()
            return True
    return False


def cancel_order_by_stuff(order_id):
    orders = Order.objects.filter(id=order_id)
    if orders.exists():
        order = orders[0]
        if order.is_actual:
            status = OrderStatus.objects.get_or_create(status='Отмена')[0]
            if order.status_id == status.id:
                order.is_actual = False
                order.save()
            pr_in_order = ProductInOrder.objects.filter(order_id=order.id)
            for prod in pr_in_order:
                count = prod.count
                size = prod.size
                prod_id = prod.product_id
                prod_on_storage = ProductOnStorage.objects.get_or_create(product_id=prod_id, size=size)
                print(prod_on_storage)
                isCreate =  prod_on_storage[1]
                prod_on_storage = prod_on_storage[0]
                if isCreate:
                    prod_on_storage.count = count
                else:
                    prod_on_storage.count += count
                prod_on_storage.save()
            return True
    return False


def get_user_orders(user_id):
    status = OrderStatus.objects.get_or_create(status='Формируется')[0]
    orders = Order.objects.raw(
        f"SELECT id, date, status_id, order_point_id, user_id FROM store_order  WHERE status_id != {status.id} AND user_id = {user_id} AND is_actual = True ORDER BY date DESC")
    orders_list = []
    for order in orders:
        pr_in_order = ProductInOrder.objects.filter(order_id=order.id)
        order_list = []
        total_sum = 0
        for prod in pr_in_order:
            product = Product.objects.get(id=prod.product_id)
            product_photo = get_product_photo(prod.product_id)
            result_cost = float(product.cost) * int(prod.count)
            result_cost = round(result_cost, 2)
            total_sum += result_cost
            product_in_order = [product.name, prod.count, prod.size, product_photo, product.cost, result_cost,
                                order.id, prod.product_id]
            order_list.append(product_in_order)
        status = get_order_status(order.id)
        point = OrderPoint.objects.get(id=order.order_point_id).name
        orders_list.append([order.id, order.date, status, point, order_list, total_sum, order.is_actual])
    return orders_list


def buy_basket(user_id, order_point_id):
    status = OrderStatus.objects.get_or_create(status='Формируется')[0]
    new_status = OrderStatus.objects.get_or_create(status='Оформлен')[0]
    order_filter = Order.objects.filter(is_actual=True, status_id=status.id, user_id=user_id)
    if order_filter.exists():
        order = order_filter[0]
        pr_in_order = ProductInOrder.objects.filter(order_id=order.id)
        date = datetime.now()
        msg = "Заказ оформлен"
        for prod in pr_in_order:
            product = Product.objects.get(id=prod.product_id)
            size = prod.size
            count = prod.count
            prods_on_storage = get_prod_on_storage(prod.product_id)
            on_storage_count = 0
            prods_on_storage_list = []
            for prod_on_storage in prods_on_storage:
                if prod_on_storage.size == size:
                    on_storage_count = prod_on_storage.count
                    prods_on_storage_list.append(prod_on_storage)
            prod_on_storage = prods_on_storage_list[0]
            if count >= on_storage_count:
                count = on_storage_count
                prod.count = count
                prod.save()
                msg = "Заказ оформлен. Некоторые товары удалены или уменьшено их количество в соответствии с наличием на складе."
            prod_on_storage.count -= count
            prod_on_storage.save()
        order.order_point_id = order_point_id
        order.status_id = new_status.id
        order.date = date
        order.save()
    else:
        msg = "Корзина пуста"
    return msg


def get_basket(user_id):
    status = OrderStatus.objects.get_or_create(status='Формируется')[0]
    order = Order.objects.filter(is_actual=True, status_id=status.id, user_id=user_id)
    basket = []
    if order.exists():
        order_id = order[0].id
        pr_in_order = ProductInOrder.objects.filter(order_id=order_id)
        for prod in pr_in_order:
            product = Product.objects.get(id=prod.product_id)
            product_photo = get_product_photo(prod.product_id)
            result_cost = float(product.cost) * int(prod.count)
            result_cost = round(result_cost, 2)
            product_in_basket = [product.name, prod.count, prod.size, product_photo, product.cost, result_cost,
                                 order_id, prod.product_id]
            basket.append(product_in_basket)
    return basket


def delete_from_order(user_id, order_id, product_id, size):
    status = OrderStatus.objects.get_or_create(status='Формируется')[0]
    order = Order.objects.filter(user_id=user_id, id=order_id, status_id=status.id)
    if order.exists():
        prod_in_order = ProductInOrder.objects.get(order_id=order_id, product_id=product_id, size=size)
        prod_in_order.delete()
        return True
    else:
        return False


def get_sum_cost(list):
    res = 0
    for it in list:
        res += it[5]
    return res


def get_size_choice(prod_id):
    sizes = []
    products_storage = get_prod_on_storage(prod_id)
    for ps in products_storage:
        sizes.append((ps.size, ps.size))
    return sizes


def get_product_photo(prod_id):
    prod_photos = ProductPhoto.objects.filter(product_id=prod_id)
    prod_ph_l = []
    for photo in prod_photos:
        p_url = photo.photo.url
        prod_ph_l.append(p_url)
    return prod_ph_l


def get_product_photo_and_id(prod_id):
    prod_photos = ProductPhoto.objects.filter(product_id=prod_id)
    prod_ph_l = []
    for photo in prod_photos:
        p_id = photo.id
        p_url = photo.photo.url
        prod_ph_l.append((p_url, p_id))
    return prod_ph_l


def del_photo(photo_id, prod_id):
    try:
        prod_photo = ProductPhoto.objects.get(id=photo_id, product_id=prod_id)
        prod_photo.delete()
        return True
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False


def get_prod_info(prod_id):
    try:
        prod_list = []
        products = Product.objects.get(id=prod_id)
        products_storage = get_prod_on_storage(prod_id)
        info = []
        for ps in products_storage:
            str_info = f"Размер: {ps.size}. Доступно {ps.count} шт."
            info.append(str_info)
        photos = get_product_photo(products.id)
        prod_list.append(photos)
        prod_list.append(products.name)
        prod_list.append(products.country)
        brand = Brand.objects.get(id=products.brand_id)
        prod_list.append(brand.name)
        prod_list.append(info)
        prod_list.append(products.cost)
        return prod_list
    except ObjectDoesNotExist:
        prod_list = [0, "Ошибка", "Некорректная ссылка"]
        return prod_list
    except MultipleObjectsReturned:
        prod_list = [0, "Ошибка", "Некорректная ссылка"]
        return prod_list


def get_count_on_storage(prod_id):
    products_storage = get_prod_on_storage(prod_id)
    count = 0
    for ps in products_storage:
        count += ps.count
    return count


def get_sizes_on_storage(prod_id):
    products_storage = get_prod_on_storage(prod_id)
    sizes = []
    for ps in products_storage:
        sizes.append(ps.size)
    return sizes


def get_all_prods_main(filter):
    if filter is None:
        products = Product.objects.all()
    else:
        products = Product.objects.filter(sub_category_id=filter)
    prods = []
    for prod in products:
        count = get_count_on_storage(prod.id)
        if count > 0:
            sizes = get_sizes_on_storage(prod.id)
            prod_list = []
            photos = get_product_photo(prod.id)
            prod_list.append(photos)
            prod_list.append(prod.name)
            prod_list.append(prod.country)
            try:
                brand = Brand.objects.get(id=prod.brand_id)
                prod_list.append(brand.name)
            except:
                brand = "None"
                prod_list.append(brand)
            prod_list.append(sizes)
            prod_list.append(count)
            prod_list.append(prod.cost)
            prod_list.append(prod.id)
            prods.append(prod_list)
    return prods


def get_order(order_id, status_text):
    result = []
    status = OrderStatus.objects.get_or_create(status=status_text)[0]
    try:
        order = Order.objects.get(id=order_id, status_id=status.id)
        result.append(True)
        result.append(order)
    except ObjectDoesNotExist:
        result.append(False)
    except MultipleObjectsReturned:
        result.append(False)
    return result


def get_storage_orders(status_text):
    status = OrderStatus.objects.get_or_create(status=status_text)[0]
    orders = Order.objects.raw(
        f"SELECT id, date, status_id, order_point_id, user_id FROM store_order  WHERE status_id = {status.id} AND is_actual = True ORDER BY date")
    count = 0
    for order in orders:
        count += 1
    return [orders, count]


def get_products_in_order(order_id):
    prods = ProductInOrder.objects.filter(order_id=order_id)
    prods_list = []
    for prod in prods:
        prod_id = prod.product_id
        product = Product.objects.get(id=prod_id)
        all_info = [product, get_product_photo(prod_id), prod.count, prod.size]
        prods_list.append(all_info)
    return prods_list


def get_order_point(point_id):
    result = []
    try:
        point = OrderPoint.objects.get(id=point_id)
        result.append(True)
        result.append(point)
    except ObjectDoesNotExist:
        result.append(False)
    except MultipleObjectsReturned:
        result.append(False)
    return result


def get_orders_delivery(point_id):
    status = OrderStatus.objects.get_or_create(status="В доставке")[0]
    delivery_orders = Order.objects.filter(status_id=status.id, order_point_id=point_id)
    orders_count = 0
    if delivery_orders.exists():
        for order in delivery_orders:
            orders_count += 1
    return [delivery_orders, orders_count]


def confirm_delivery(order_id):
    status = OrderStatus.objects.get_or_create(status="В доставке")[0]
    new_status = OrderStatus.objects.get_or_create(status='Готов к выдаче')[0]
    try:
        order = Order.objects.get(id=order_id, status_id=status.id)
        order.status_id = new_status.id
        order.date = datetime.now()
        order.save()
        result = True
    except ObjectDoesNotExist:
        result = False
    except MultipleObjectsReturned:
        result = False
    return result


def get_order_point_orders(point_id):
    status = OrderStatus.objects.get_or_create(status="Готов к выдаче")[0]
    orders = Order.objects.raw(
        f"SELECT id, date, status_id, order_point_id, user_id FROM store_order  WHERE status_id = {status.id} AND is_actual = True AND order_point_id = {point_id}")
    count = 0
    for order in orders:
        count += 1
    return [orders, count]


def change_prod_in_order(prod_id, order_id, size, cancel_count):
    try:
        order = Order.objects.get(id=order_id, is_actual=True)
        prod_in_order = ProductInOrder.objects.get(product_id=prod_id, order_id=order_id, size=size)
        point_id = order.order_point_id
        user_id = order.user_id
        if cancel_count >= prod_in_order.count:
            prod_in_order.delete()
        else:
            prod_in_order.count -= cancel_count
            prod_in_order.save()
        status = OrderStatus.objects.get_or_create(status="Отмена")[0]
        cancel_order = \
            Order.objects.get_or_create(user_id=user_id, status_id=status.id, is_actual=True, order_point_id=point_id)[
                0]
        cancel_prods_list = ProductInOrder.objects.get_or_create(product_id=prod_id, order_id=cancel_order.id,
                                                                 size=size)
        cancel_prods = cancel_prods_list[0]
        if cancel_prods_list[1]:
            cancel_prods.count = cancel_count
        else:
            cancel_prods.count += cancel_count
        cancel_order.date = datetime.now()
        cancel_order.save()
        cancel_prods.save()
        if not ProductInOrder.objects.filter(order_id=order_id).exists():
            order.delete()
        result = True
    except ObjectDoesNotExist:
        result = False
    except MultipleObjectsReturned:
        result = False
    return result


def give_order(order_id):
    status = OrderStatus.objects.get_or_create(status="Готов к выдаче")[0]
    new_status = OrderStatus.objects.get_or_create(status='Закрыт')[0]
    try:
        order = Order.objects.get(id=order_id, status_id=status.id)
        order.status_id = new_status.id
        order.date = datetime.now()
        order.is_actual = False
        order.save()
        result = True
    except ObjectDoesNotExist:
        result = False
    except MultipleObjectsReturned:
        result = False
    return result


def get_prod_count_in_order(prod_id, order_id, size):
    result = []
    try:
        order = Order.objects.get(id=order_id, is_actual=True)
        prod_in_order = ProductInOrder.objects.get(product_id=prod_id, order_id=order_id, size=size)
        count = prod_in_order.count
        result = [True, count]
    except ObjectDoesNotExist:
        result.append(False)
    except MultipleObjectsReturned:
        result.append(False)
    return result


def get_brands():
    brands = Brand.objects.all()
    result = []
    for brand in brands:
        result.append((brand.id, brand))
    return result


def add_product(name, country, brand_id, cost, sex, sub_category_id=None):
    try:
        prod = Product.objects.create(name=name, country=country, brand_id=brand_id, cost=cost, sex=sex,
                                      sub_category_id=sub_category_id)
        id = prod.id
        return [True, id]
    except Exception:
        return [False]


def get_all_prods():
    prods = Product.objects.all()
    result = []
    for prod in prods:
        try:
            brand = Brand.objects.get(id=prod.brand_id)
        except:
            brand = "None"
        result.append([get_product_photo(prod.id), prod.id, prod.name, brand, prod.cost])
    return result


def get_prods_by_id(id):
    result = []
    prods = Product.objects.filter(id=id)
    if prods.exists():
        for prod in prods:
            brand = Brand.objects.get(id=prod.brand_id)
            result.append([get_product_photo(prod.id), prod.id, prod.name, brand, prod.cost])
    return result


def is_storage_stuff(user_id):
    try:
        stuff = StuffCategory.objects.get(user_id=user_id, is_storage_stuff=True)
        return True
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False


def is_point_stuff(user_id):
    try:
        stuff = StuffCategory.objects.get(user_id=user_id, is_point_stuff=True)
        return True
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False


def get_sub_categories():
    s_c = SubCategory.objects.all()
    result = []
    for category in s_c:
        result.append((category.id, category.name))
    return result


def get_categories():
    c = []
    for obj in Category.objects.all():
        dict = {
            'id': obj.id,
            'name': obj.name,
        }
        c.append(dict)
    categories = json.dumps(c, indent=4)
    s_c = []
    for obj in SubCategory.objects.all():
        dict = {
            'id': obj.id,
            'name': obj.name,
            'category': obj.category_id,
        }
        s_c.append(dict)
    sub_categories = json.dumps(s_c, indent=4)

    return [categories, sub_categories]


def add_on_storage(prod_id, count, size):
    prod = ProductOnStorage.objects.filter(product_id=prod_id, size=size)
    if prod.exists():
        prod = prod[0]
        if prod.count + count <= 0:
            prod.count = 0
        else:
            prod.count = prod.count + count
        prod.save()
    else:
        new_prod = ProductOnStorage.objects.create(product_id=prod_id, size=size, count=count)


def del_from_storage(id, prod_id):
    try:
        prod = ProductOnStorage.objects.get(id=id, product_id=prod_id)
        prod.delete()
        return True
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False

def del_category(id):
    try:
        cat = Category.objects.get(id=id)
        cat.delete()
        return True
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False

def del_sub_category(id, cat_id):
    try:
        sub_cat = SubCategory.objects.get(id=id, category_id=cat_id)
        sub_cat.delete()
        return True
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False


def del_brand(id):
    try:
        brand = Brand.objects.get(id=id)
        brand.delete()
        return True
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False