import random
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Conf_code
from .forms import UserRegisterForm, ConfirmCodeForm
from django.core.mail import send_mail
from django.contrib.auth.models import User


def send_m(request):
    if request.method == 'POST':
        form = ConfirmCodeForm(request.POST)
        if form.is_valid():
            user_id = request.GET.get("id")
            code_all = Conf_code.objects.filter(user_id=user_id, is_actual=True)
            code = code_all[0].code
            user = User.objects.get(id=user_id)
            user_code = form.cleaned_data.get('conf_code')
            if user_code == code:
                user.is_active = True
                user.save()
                code_all = Conf_code.objects.filter(user_id=user_id, is_actual=True).update(is_actual=False)
                return redirect('/accounts/login/')
            else:
                msg = "Неправильный код"
                return render(request, 'conf_email.html', {'form': form, 'msg': msg})

    else:
        form = ConfirmCodeForm(request.POST)
        msg = "Введите код с почты"
        return render(request, 'conf_email.html', {'form': form, 'msg': msg})


def reg(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=form.cleaned_data.get('email')).exists():
                return render(request, 'register.html', {'form': form, "msg": "Почта уже занята"})
            else:
                user = form.save(commit=False)
                user.is_active = False
                code = Conf_code()
                code.is_actual = True
                conf_code = ''
                for i in range(0, 4):
                    conf_code += str(random.randint(0, 9))
                code.code = conf_code
                user.save()
                code.user_id = user.id
                code.save()
                send_mail('Подтвердите свой электронный адрес',
                          f'Пожалуйста, скопируйте код, чтобы подтвердить свой адрес электронной почты: {conf_code}'
                          , 'shop.5tore@yandex.ru',
                          recipient_list=[email], fail_silently=False)
                return redirect(f'confirm_email/?id={user.id}')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})
