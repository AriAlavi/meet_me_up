from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from main.models import Profile, Event

def event(request, code_name):
    event = Event.objects.get(code_name=code_name)
    context = {
        'event': event
    }
    return render(request, "main/event.html", context)

def home(request):
    context = {
    }
    return render(request, "main/home.html", context)

def index(request):
    context = {
        'event': Event.objects.filter(creator=request.user.profile)
    }
    return render(request, "main/index.html", context)

def profile(request):
    messages.success(request, "Logged in successfully!")
    return redirect('home')

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            user = form.save()
            profile = Profile()
            profile.user = user
            profile.save()
            return redirect('')
        else:
            for error in form.errors.items():
                messages.warning(request, error)

    context = {
        'form' : form
    }
    return render(request, "main/register.html", context)

def busy(request):
    context = {

    }
    return render(request, "main/busy.html", context)