from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from coursework.models import Key, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect

def registration_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        data_error = False

        if User.objects.filter(email=email).exists():
            data_error = True
            messages.error(request, 'Email already exists')

        if len(password) < 8:
            data_error = True
            messages.error(request, 'Password must be at least 8 characters')

        if data_error:
            return redirect('registration')

        else:
            new_user = User.objects.create_user(name=name, surname=surname ,email=email, password=password)
            messages.success(request, 'User created successfully')
            return redirect('login')

    return render(request, 'registration_page.html')

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email or password is incorrect')
            return redirect('login')

    return render(request, 'login_page.html')

@login_required
def logout_page(request):
    logout(request)
    return redirect('login')

@login_required
def home_page(request):
    users_keys = Key.objects.filter(holder=request.user)
    return render(request, 'home_page.html', {'users_keys': users_keys})

@login_required
def key_list(request):
    keys = Key.objects.all()
    return render(request, 'key_list.html', {'keys': keys, 'user': request.user})

@login_required
def take_key(request, key_id):
    try:
        key = Key.objects.get(id=key_id)
    except Key.DoesNotExist:
        raise Http404("Key does not exist")
    try:
        key.take_key(request.user)
        messages.success(request, f"Key taken for this auditory {key.auditory}")
    except ValueError as e:
        messages.error(request, e)
    # referer = request.META.get('HTTP_REFERER')
    # return HttpResponseRedirect(referer)
    return redirect('home')

@login_required
def put_key(request, key_id):
    try:
        key = Key.objects.get(id=key_id)
    except Key.DoesNotExist:
        raise Http404("Key does not exist")
    try:
        key.put_key()
        messages.success(request, f"Key put for this auditory {key.auditory}")
    except ValueError as e:
        messages.error(request, e)
    return redirect('home')


@login_required
def transfer_key(request, key_id):
    try:
        key = Key.objects.get(id=key_id)
    except Key.DoesNotExist:
        messages.error(request, 'Ключ не знайдено.')
        return redirect('transfer_key')

    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        try:
            new_holder = User.objects.get(name=name, surname=surname)
        except User.DoesNotExist:
            messages.error(request, 'Username does not exist')
            redirect('transfer_key')

        try:
            key.transfer_key(new_holder)
            messages.success(request, 'Key transferred successfully to user {user.name} {user.surname}')
            return redirect('home')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('transfer_key')

    return render(request, 'transfer_page.html')

@login_required
def free_keys(request):
    free_keys = Key.objects.filter(status='free')
    return render(request, 'free_keys_page.html', {'free_keys': free_keys})

@login_required
def profile(request):
    return render(request, 'profile_page.html', {'user': request.user}  )

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        # user.name = request.POST['name']
        # user.surname = request.POST['surname']
        user.email = request.POST['email']
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, 'Профіль оновлено успішно.')
        return redirect('home')
    return render(request, 'edit_profile_page.html')
#
# @login_required
# def request_key(request, key_id):
#     key = get_object_or_404(Key, id=key_id)
#     if key.status == 'taken':
#         messages.error(request, 'Аудиторія вже зайнята')
#         return redirect('home')
#
#     existing = Key_requests.objects.filter(user=request.user, key=key, is_approved=False, is_expired=False).first()
#     if existing:
#         messages.warning(request, "Ви вже надіслали запит на цей ключ")
#         return redirect('home')
#
#     Key_requests.objects.create(user=request.user, key=key)
#     messages.success(request, "Запит на отримання ключа надіслано адміністратору")
#     return redirect('home')
#
# @staff_member_required
# def manage_requests(request):
#     requests = Key_requests.objects.filter(is_expired=False, is_approved=False)
#
#     for req in requests:
#         if not req.is_valid():
#             req.is_expired = True
#             req.save()
#     return render(request, 'admin_key_requests.html', {'requests': requests})
#
# @staff_member_required
# def approve_request(request, request_id):
#     req = get_object_or_404(Key_requests, id=request_id)
#
#     if not req.is_valid():
#         req.is_expired = True
#         req.save()
#         messages.error(request, "Запит більше не дійсний.")
#         return redirect('manage_requests')
#
#     try:
#         req.key.take_key(req.user)
#         req.is_approved = True
#         req.save()
#         messages.success(request, "Запит підтверджено.")
#     except ValueError as e:
#         messages.error(request, str(e))
#
#     return redirect('manage_requests')