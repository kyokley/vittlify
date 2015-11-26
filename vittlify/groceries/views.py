from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .forms import SignInForm

def index(request):
    return HttpResponse("Hello, world. You're at the vittlify index.")

def home(request):
    template = loader.get_template('groceries/home.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

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

            if user and request.POST.has_key('next'):
                return HttpResponseRedirect(request.POST['next'])
            return render(request, 'groceries/signin.html', context)
    else:
        form = SignInForm()

    return render(request, 'groceries/signin.html', {'form': form})
