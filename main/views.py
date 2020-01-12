from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from main.models import Profile, Event, Free

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
    if request.POST:
        DATA_TYPES = ["setFree"]
        try:
            data_type = request.POST['data_type']
        except:
            return HttpResponseBadRequest("data_type is required")
        if data_type not in DATA_TYPES:
            return HttpResponseBadRequest("{} is not a valid data type. Pick from: {}".format(data_type, DATA_TYPES))
        if data_type == "setFree":
            try:
                free_array = request.POST["free_array"]
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
            except:
                return HttpResponseBadRequest("free_array, start_date, and end_date is required")
            try:
                free_array = json.loads(free_array)
            except Exception:
                return HttpResponseBadRequest("free_array not formatted correctly")
            try:
                start_date = datetime.strptime(start_date, "%m/%d/%Y")
                end_date = datetime.strptime(end_date, "%m/%d/%Y")
            except:
                return HttpResponseBadRequest("dates must be in m/d/Y form")
            expected_bit = 0
            i = 0
            # print("FULL LIST:", free_array)
            last_date = start_date
            for dt in Free.timeGenerator(start_date, end_date, timedelta(minutes=30)):
                # print("[{}] actual[{}] given i[{}] DATE TIME:".format(expected_bit, free_array[i], i), dt)
                if expected_bit != free_array[i]:
                    if expected_bit == 1:
                        # print("flip free")
                        free = Free(profile=request.user.profile, start_date=last_date, end_date=dt)
                        free.save()
                        expected_bit = 0
                    else:
                        # print("flip delete")
                        Free.objects.filter(profile=request.user.profile).filter(start_date__gte=last_date).filter(end_date__gte=dt).delete()
                        expected_bit = 1
                    last_date = dt
                i += 1
            return HttpResponse()

            # i = 0
            # freeList = []
            # for dt in Free.timeGenerator(start_date, end_date, timedelta(minutes=30)):
            #     local_end = start_date + timedelta(minutes=30)
            #     if free_array[i] == i:
            #         free = Free(profile=request.user.profile, start_date=dt, end_date=local_end)
            #         free.append(freeList)

            #     i += 1
            # [x.save() for x in freeList]
            # return HttpResponse()
        return HttpResponseBadRequest("{} is not declared".format(data_type))
    else:
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