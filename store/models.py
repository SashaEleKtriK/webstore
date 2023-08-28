from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=15)


class SubCategory(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=15)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Brand(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=15)


class Product(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=15)
    country = models.CharField(max_length=15)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    cost = models.DecimalField(decimal_places=2, max_digits=10)
    sex = models.CharField(max_length=15)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='products/')


class OrderPoint(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=15)


class ProductOnStorage(models.Model):
    def __str__(self):
        return str(self.product) + ", size: " + str(self.size)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=15)
    count = models.IntegerField(null=True)


class OrderStatus(models.Model):
    def __str__(self):
        return self.status

    status = models.CharField(max_length=15)


class Order(models.Model):
    def __str__(self):
        return str(self.id)

    order_point = models.ForeignKey(OrderPoint, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    is_actual = models.BooleanField()


class ProductInOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    count = models.IntegerField(null=True)
    size = models.CharField(max_length=15)


class StuffCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_storage_stuff = models.BooleanField()
    is_point_stuff = models.BooleanField()
    order_point = models.ForeignKey(OrderPoint, on_delete=models.CASCADE, null=True)


