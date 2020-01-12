from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect, reverse

from main.words import randomSentence
from main.models import Profile, Event, Free
from main.forms import *
from datetime import datetime, timedelta
import json

@login_required
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

@login_required
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
        DATA_TYPES = ["setFree", "joinEvent"]
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
        elif data_type == "joinEvent":
            try:
                event_url = request.POST['event_url']
            except:
                return HttpResponseBadRequest("event_url is required")
            try:
                event = Event.objects.get(code_name=event_url)
            except:
                return HttpResponseBadRequest("'{}' is not a valid event url".format(event_url))
            request.user.profile.events.add(event)
            return HttpResponse()

        return HttpResponseBadRequest("{} is not declared".format(data_type))
    else:
        DATA_TYPES = ["getFree", "getEventFree", "getEventHeatmap"]
        try:
            data_type = request.GET["data_type"]
        except:
            return HttpResponseBadRequest("data_type is required")
        if data_type not in DATA_TYPES:
            return HttpResponseBadRequest("{} is not a valid data type. Pick from: {}".format(data_type, DATA_TYPES))
        



        if data_type == "getFree":
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
            return HttpResponse(json.dumps(request.user.profile.getFreeArray(start_date, end_date)))
        elif data_type == "getEventFree" or data_type == "getEventHeatmap":
            try:
                event = request.GET['event']
            except:
                return HttpResponseBadRequest("event argument required")
            try:
                event = Event.objects.get(code_name=event)
            except:
                return HttpResponseNotFound("{} is not a valid event".format(event))
            if data_type == "getEventFree":
                results = {}
                for profile in event.profile_set.all():
                    results[profile.id] = profile.getFreeArray(event.start_date, event.end_date)
                return HttpResponse(json.dumps(results))
            elif data_type == "getEventHeatmap":
                return HttpResponse(json.dumps(event.getOverlapHeatMap()))

        else:
            raise Exception("Logic error")

        return HttpResponseBadRequest("{} is not declared in the interface".format(data_type))    

@login_required
def free(request):
        
    context = {

    }
    return render(request, "main/free.html", context)

@login_required
def create(request):
    if request.POST:
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        name = request.POST['event_name']
        url = request.POST['event_url']
        length = request.POST['length']

        REQUIRED_FIELDS = {
            "Start date" : start_date,
            "End date" : end_date,
            "Name" : name,
            "Length" : length
        }

        error = []
        for key, value in REQUIRED_FIELDS.items():
            if not value:
                error.append(key + " is a required field")
        if error:
            for e in error:
                messages.warning(request, e)
            return render(request, "main/create.html") 
        try:
            length = float(length)
        except:
            messages.warning(request, "length must be a string")
            return render(request, "main/create.html")

        if length < .5 or length > 24:
            messages.warning(request, "length cannot be less than .5 or greater than 24 hours")
            return render(request, "main/create.html")
        if length % .5:
            messages.warning(request, "length must be in interval of 30 minutes")
            return render(request, "main/create.html")
        if end_date < start_date:
            temp = start_date
            start_date = end_date
            end_date = temp
        try:
            start_date = datetime.strptime(start_date, "%m/%d/%Y %H:%M:%S")
            end_date = datetime.strptime(end_date, "%m/%d/%Y %H:%M:%S")
        except:
            messages.warning(request, "start_date or end_date are incorrectly formatted")
            return render(request, "main/create.html")
        if not url:
            while True:
                url = randomSentence(30, 50)
                if Event.objects.filter(code_name=url).count() == 0:
                    break

        else:
            if Event.objects.filter(code_name=url).count() > 0:
                message.warning(request, "url '{}' is already taken".format(url))
                return render(request, "main/create.html")

        event = Event(start_date=start_date, end_date=end_date, title=name, code_name=url, length = length)
        event.creator = request.user.profile
        event.save()
        request.user.profile.events.add(event)
        messages.success(request, "Event '{}' created".format(url))
        return redirect("event", code_name=event.code_name)
        
        # try:

        # except:
        #     messages.warning(request, "start_date, end_date, event_name, and event_url are required arguments")
        #     return render(request, "main/create.html")
        # try:
        #     start_date = datetime.strptime(start_date, "%m/%d/%Y %H:%M:%S")
        #     end_date = datetime.strptime(end_date, "%m/%d/%Y %H:%M:%S")
        # except:
        #     if not start_date or end_date:
        #         messages.warning(request, "start_date and end_date are required fields")
        #         return HttpResponse("location.reload()")
        #     return HttpResponse("date is in bad format, must be m/d/Y H:M:S")

        # if not name:
        #     messages.warning(request, "name is a required field")
        #     return HttpResponse("location.reload()")
        # try:
        #     Event.objects.get(code_name=url)
        #     messages.warning(request, "url '{}' already exists".format(url))
        #     return HttpResponse("location.reload()")
        # except:
        #     pass
        # try:

        #     return HttpResponse("window.replace(" + url + ")")
        # except Exception as e:
        #     messages.warning(request, str(e))
        #     return HttpResponse("location.reload()")

        # return event.code_name

    return render(request, "main/create.html")