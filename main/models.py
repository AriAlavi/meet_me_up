from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timedelta
from math import floor
import pytz

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    events = models.ManyToManyField("main.Event", blank=True)

    
    def getFreeInterval(self, start_date, end_date):
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        return self.free_set.filter(start_date__gte=start_date).filter(end_date__lte=end_date)
    
    def getFreeArray(self, start_date, end_date, interval=timedelta(minutes=30)):
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        assert isinstance(interval, timedelta)
        start_date = Free.makeTimezoneAware(start_date)
        end_date = Free.makeTimezoneAware(end_date)
        freeArray = []
        for x in Free.timeGenerator(Free.makeTimezoneAware(start_date), Free.makeTimezoneAware(end_date), interval):
            freeArray.append(0)
        print("ARRAY LENGTH:", len(freeArray))
        def calculateIndex(start_date, interval, calculateDate):
            assert isinstance(start_date, datetime)
            assert isinstance(interval, timedelta)
            assert isinstance(calculateDate, datetime)
            print("CALC INDEX:", start_date, ", ", calculateDate, ", ", floor((calculateDate-start_date)/interval))
            return floor((calculateDate-start_date)/interval)

        for freeObject in self.getFreeInterval(start_date, end_date):
            for freeRange in Free.timeGenerator(freeObject.start_date, freeObject.end_date, interval):
                freeArray[calculateIndex(start_date, interval, freeRange)] = 1

        return freeArray
            
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


class Free(models.Model):
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
    def makeTimezoneAware(givenDate):
        assert isinstance(givenDate, datetime)
        if givenDate.tzinfo is not None and givenDate.tzinfo.utcoffset(givenDate) is not None:
            return givenDate
        return givenDate.replace(tzinfo=pytz.timezone("UTC")) 

    def __str__(self):
        return "From {} to {}".format(self.start_date, self.end_date)

    
        

            
