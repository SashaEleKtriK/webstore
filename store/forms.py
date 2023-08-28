from django import forms

from .models import OrderPoint, Product, ProductPhoto, ProductOnStorage, Category, SubCategory, Brand
from .utils import get_size_choice, get_brands, get_sub_categories


class ProductToOrder(forms.Form):

    def __init__(self, prod_id, *args, **kwargs):
        super(ProductToOrder, self).__init__(*args, **kwargs)
        self.fields['size'].choices = get_size_choice(prod_id)

    size = forms.ChoiceField(choices=(), required=True)
    count = forms.IntegerField(min_value=1, max_value=10)


class OrderPoints(forms.Form):
    points = forms.ModelChoiceField(queryset=OrderPoint.objects.all(), to_field_name="id")


class CancelProductInOrder(forms.Form):

    def __init__(self, all_count, *args, **kwargs):
        super(CancelProductInOrder, self).__init__(*args, **kwargs)
        choice_list = []
        for i in range(1, all_count + 1):
            choice_list.append((i, i))
        self.fields['count'].choices = choice_list

    count = forms.ChoiceField(choices=(), required=True)


class AddProduct(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AddProduct, self).__init__(*args, **kwargs)
        self.fields['brand'].choices = get_brands()
        self.fields['sub_category'].choices = get_sub_categories()

    brand = forms.ChoiceField(choices=(), required=True)
    sex = forms.ChoiceField(choices=[('male', 'male'), ('female', 'female'), ('all', 'all')], required=True)
    sub_category = forms.ChoiceField(choices=(), required=False)
    name = forms.CharField(max_length=15)
    country = forms.CharField(max_length=15)
    cost = forms.DecimalField(decimal_places=2, max_digits=10)


class Search(forms.Form):
    quest = forms.IntegerField(min_value=1)


class AddPhoto(forms.ModelForm):
    class Meta:
        model = ProductPhoto
        fields = ('product', 'photo')


class AddToStorage(forms.ModelForm):
    class Meta:
        model = ProductOnStorage
        fields = ('product', 'count', 'size')


class AddToCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)


class AddToSubCategory(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ('name', 'category')

class AddBrand(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ('name',)
