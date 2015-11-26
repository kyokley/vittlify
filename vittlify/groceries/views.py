from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

def index(request):
    return HttpResponse("Hello, world. You're at the vittlify index.")

def home(request):
    template = loader.get_template('groceries/home.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def signin(request):
    context = {}
    user = None

    if request.GET.has_key('next'):
        context['next'] = request.GET['next']

    try:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is None:
                raise Exception('Invalid User')
            else:
                if user.is_active:
                    login(request, user)
                    context['loggedin'] = True
                    context['user'] = request.user
    except Exception:
        context['error_message'] = 'Incorrect username or password!'

    if user and request.POST.has_key('next'):
        return HttpResponseRedirect(request.POST['next'])

    return render(request, 'groceries/signin.html', context)
