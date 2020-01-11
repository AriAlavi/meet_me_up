from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from main.models import Profile, Event, Busy

from datetime import datetime, timedelta
import json

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
            return redirect("")
        else:
            for error in form.errors.items():
                messages.warning(request, error)

    context = {
        'form' : form
    }
    return render(request, "main/register.html", context)


@login_required
def busyInterface(request):
    DATA_TYPES = ["getFree", "setBusy"]
    try:
        data_type = request.POST["data_type"]
    except:
        return HttpResponseBadRequest("data_type is required")
    if data_type not in DATA_TYPES:
        return HttpResponseBadRequest("{} is not a valid data type. Pick from: {}".format(data_type, DATA_TYPES))
    if data_type == "getFree":
        try:
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
        except:
            return HttpResponseBadRequest("start_date and end_date required")

        try:
            start_date = datetime.strptime(start_date, "%m/%d/%Y")
            end_date = datetime.strptime(end_date, "%m/%d/%Y")
        except:
            return HttpResponseBadRequest("Date must be in format m/d/Y")

        return HttpResponse(json.dumps(Busy.getFree([request.user.profile], start_date, end_date)))

    if data_type == "setBusy":
        try:
            start_date = request.POST['start_date']
            available_array = request.POST['available_array']
        except:
            return HttpResponseBadRequest("start_date and available_array is required")
        try:
            start_date = datetime.strptime(start_date, "%m/%d/%Y")
        except:
            return HttpResponseBadRequest("Date must be in format m/d/Y")
        try:
            available_array = json.loads(available_array)
        except:
            return HttpResponseBadRequest("available array must be json")
        
        for available in available_array:
            if available:
                Busy.objects.filter(start_date__gte=available).filter(end_date__lte)
            start_date += timedelta(minutes=30)

@login_required
def busy(request):
        
    context = {

    }
    return render(request, "main/busy.html", context)