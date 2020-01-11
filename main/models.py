from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timedelta

import pytz

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.user)

class Event(models.Model):
    code_name = models.SlugField(unique=True, max_length=50)
    title = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    def __str__(self):
        return self.title + " at " + str(self.start_date) + " to " + str(self.end_date) + " created by " + str(self.creator)

class Busy(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    @staticmethod
    def timeGenerator(current_time, end_time, step):
        assert isinstance(current_time, datetime)
        assert isinstance(end_time, datetime)
        assert isinstance(step, timedelta)
        while end_time > current_time:
            yield current_time
            current_time +=  step

    @staticmethod
    def getBusy(profile, start_date, end_date):
        assert isinstance(profile, Profile)
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)

        return Busy.objects.filter(profile=profile).filter(start_date__gte=start_date).filter(end_date__lte=end_date)

    @staticmethod
    def makeTimezoneAware(givenDate):
        assert isinstance(givenDate, datetime)
        if givenDate.tzinfo is not None and givenDate.tzinfo.utcoffset(d) is not None:
            return givenDate
        return givenDate.replace(tzinfo=pytz.timezone("UTC")) 
        


    @staticmethod
    def getFree(profileList, start_date, end_date):
        assert isinstance(profileList, list)
        assert all(isinstance(x, Profile) for x in profileList)
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        start_date = Busy.makeTimezoneAware(start_date)
        end_date = Busy.makeTimezoneAware(end_date)

        busyPeriods = {}
        freePeriods = []
        for profile in profileList:
            busyPeriods[profile] = Busy.getBusy(profile, start_date, end_date)
        
        for time in Busy.timeGenerator(start_date, end_date, timedelta(minutes=30)):
            thisHourFree = []
            print("TIME:", time)
            for profile, busyList in busyPeriods.items():
                print("BUSY LIST:", busyList)
                if not any(x for x in busyList if x.start_date < time < x.end_date):
                    thisHourFree.append(profile)

            freePeriods.append(thisHourFree)

        return freePeriods


    def __str__(self):
        return "From {} to {}".format(self.start_date, self.end_date)

    
        

            
