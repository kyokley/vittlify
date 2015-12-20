from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from .forms import SignInForm
from .models import (Shopper,
                     RecentlyCompletedShoppingList,
                     ShoppingList,
                     ShoppingListMember,
                     )

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

    if not user or not user.is_authenticated():
        return HttpResponseRedirect('/vittlify')

    context['loggedin'] = True
    context['owner'] = Shopper.objects.filter(user=user).first()
    owned_lists = list(Shopper.objects.filter(user=user)
                                      .first()
                                      .owned_lists
                                      .all())
    context['owned_lists'] = owned_lists
    context['shoppers'] = [shopper for shopper in Shopper.objects.select_related('user').all()
                                if shopper.user != user]
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

def shared_lists(request, shopper_id):
    if request.method == 'GET':
        owner = Shopper.objects.filter(user=request.user).first()
        owned_lists = set(owner.owned_lists.all())

        shopper = Shopper.objects.get(pk=shopper_id)

        selected = set()

        for owned_list in owned_lists:
            if owned_list in shopper.shopping_lists.all():
                selected.add(owned_list)

        unselected = owned_lists.difference(selected)
        data = {'selected': [x.as_dict() for x in selected],
                'unselected': [x.as_dict() for x in unselected]}
        return JsonResponse(data)

def shared_list_member_json(request, shopper_id, list_id):
    owner = Shopper.objects.filter(user=request.user).first()
    shopping_list = ShoppingList.objects.get(pk=list_id)

    if owner != shopping_list.owner:
        raise ValueError('User is not the owner of the requested shopping list')

    shopper = Shopper.objects.get(pk=shopper_id)
    slm = (ShoppingListMember.objects
                             .filter(shopper=shopper)
                             .filter(shopping_list=shopping_list)
                             .first())

    if request.method == 'POST':
        if not slm:
            slm = ShoppingListMember.objects.create(**{'shopper': shopper,
                                                       'shopping_list': shopping_list})
            return JsonResponse(slm.as_dict(), status=201)
        else:
            return JsonResponse(slm.as_dict(), status=200)
    elif request.method == 'DELETE':
        if not slm:
            return JsonResponse(slm.as_dict(), status=200)
        else:
            return JsonResponse(status=204)
