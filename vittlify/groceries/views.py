from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from .forms import SignInForm
from .models import Shopper, RecentlyCompletedShoppingList

def home(request):
    context = {'loggedin': False}
    user = request.user
    if user and user.is_authenticated():
        context['loggedin'] = True

        shopping_lists = list(Shopper.objects.filter(user=user).first().shopping_lists.all())
        context['shopping_lists'] = shopping_lists
        recently_completed_list = RecentlyCompletedShoppingList(user)
        context['shopping_lists'].append(recently_completed_list)
    return render(request, 'groceries/home.html', context)

def settings(request):
    context = {'loggedin': False}
    user = request.user
    if user and user.is_authenticated():
        context['loggedin'] = True
        owned_lists = list(Shopper.objects.filter(user=user)
                                          .first()
                                          .owned_lists
                                          .all())
        context['owned_lists'] = owned_lists
    return render(request, 'groceries/settings.html', context)

def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            context = {}
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user and user.is_active:
                login(request, user)
                context['loggedin'] = True
                context['user'] = request.user
            else:
                raise Exception('Invalid User')

            if user and 'next' in request.POST:
                return HttpResponseRedirect(request.POST['next'])
            return HttpResponseRedirect('/vittlify')
    else:
        form = SignInForm()

    return render(request, 'groceries/signin.html', {'form': form})

def signout(request):
    logout(request)
    context = {}
    return render(request, 'groceries/signout.html', context)
