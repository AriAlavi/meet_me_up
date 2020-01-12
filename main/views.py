from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from main.models import Profile, Event

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
        'event': request.user.profile.events.all()
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
            return redirect('login')
        else:
            for error in form.errors.items():
                messages.warning(request, error)

    context = {
        'form' : form
    }
    return render(request, "main/register.html", context)

@login_required
def freeInterface(request):
    DATA_TYPES = ["getFree", "getEventFree"]
    try:
        data_type = request.GET["data_type"]
    except:
        return HttpResponseBadRequest("data_type is required")
    if data_type not in DATA_TYPES:
        return HttpResponseBadRequest("{} is not a valid data type. Pick from: {}".format(data_type, DATA_TYPES))
    
    if data_type == "getFree" or data_type == "getEventFree":
        try:
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']
        except:
            return HttpResponseBadRequest("start_date and end_date arguments required")
        try:
            start_date = datetime.strptime(start_date, "%m/%d/%Y")
            end_date = datetime.strptime(end_date, "%m/%d/%Y")
        except:
            return HttpResponseBadRequest("dates must be in m/d/Y form")

        if data_type == "getFree":
            return HttpResponse(json.dumps(request.user.profile.getFreeArray(start_date, end_date)))
        elif data_type == "getEventFree":
            try:
                event = request.GET['event']
            except:
                return HttpResponseBadRequest("event argument required")
            try:
                event = Event.objects.get(code_name=event)
            except:
                return HttpResponseNotFound("{} is not a valid event".format(event))
            results = {}
            for profile in event.profile_set.all():
                results[profile.id] = profile.getFreeArray(start_date, end_date)
            return HttpResponse(json.dumps(results))

        else:
            raise Exception("Logic error")

    return HttpResponseBadRequest("{} is not declared in the interface".format(data_type))
    

# @login_required
# def busyInterface(request):
#     DATA_TYPES = ["getFree", "setBusy"]


#     if data_type == "getFree":
#         try:
#             start_date = request.GET['start_date']
#             end_date = request.GET['end_date']
#         except:
#             return HttpResponseBadRequest("start_date and end_date required")

#         try:
#             start_date = datetime.strptime(start_date, "%m/%d/%Y")
#             end_date = datetime.strptime(end_date, "%m/%d/%Y")
#         except:
#             return HttpResponseBadRequest("Date must be in format m/d/Y")

#         return HttpResponse(json.dumps(Busy.getFree([request.user.profile], start_date, end_date)))

#     if data_type == "setBusy":
#         try:
#             start_date = request.GET['start_date']
#             available_array = request.GET['available_array']
#         except:
#             return HttpResponseBadRequest("start_date and available_array is required")
#         try:
#             start_date = datetime.strptime(start_date, "%m/%d/%Y")
#         except:
#             return HttpResponseBadRequest("Date must be in format m/d/Y")
#         try:
#             available_array = json.loads(available_array)
#         except:
#             return HttpResponseBadRequest("available array must be json")
        
#         for available in available_array:
#             if available:
#                 Busy.objects.filter(start_date__gte=available).filter(end_date__lte)
#             start_date += timedelta(minutes=30)

@login_required
def busy(request):
        
    context = {

    }
    return render(request, "main/busy.html", context)

@login_required
def create(request):
    context = {

    }
    return render(request, "main/create.html", context)