from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from wypozyczalnia.models import OrderItem, Order, Review
from django.utils import timezone
from django.contrib.auth.models import User


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Stworzono konto! Możesz się zalogować.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


# edycja profilu
@login_required
def profile_edit(request):  # w tej funkcji od razu jest update użytkownika i profilu
    if request.method == 'POST':
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if p_form.is_valid and u_form.is_valid:
            p_form.save()
            u_form.save()
            messages.success(request, f'Dane zmodyfikowane')
            return redirect('profile-view')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
        u_form = UserUpdateForm(instance=request.user)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile_edit.html', context)


# widok profilu
# stworzyć warunek sprawdzający czy książki sa aktualnie wyporzyczone przez użytkownika i niech to pokazuje na profilu
@login_required()
def profile_view(request):
    user = request.user
    order_qs = Order.objects.filter(user=user)
    time_now = timezone.now()
    if order_qs.exists():
        order = order_qs[0]
        order_items = OrderItem.objects.filter(
            user=user).order_by('-ordered_date')
        # wypuszczam tylko recenzje danego użytkownika
        reviews = Review.objects.filter(
            review_author=user).order_by('-review_date')
        borrowed_items = order.items.all().order_by('-ordered_date')
        return render(request, 'users/profile.html', {'user': user,
                                                      'order_items': order_items,
                                                      "borrowed_items": borrowed_items,
                                                      'reviews': reviews,
                                                      'time_now': time_now,
                                                      })
    else:
        return render(request, 'users/profile.html')


# tu jest jakis problem dlatego mi wyświetla w navbarze jakby był zalogowany
def profile_preview(request, username):
    users = User.objects.filter(username=username)
    reviews = Review.objects.all()
    return render(request, 'users/profile_preview.html', {'users': users, 'reviews': reviews})
