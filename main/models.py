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
        # print("ARRAY LENGTH:", len(freeArray))
        def calculateIndex(start_date, interval, calculateDate):
            assert isinstance(start_date, datetime)
            assert isinstance(interval, timedelta)
            assert isinstance(calculateDate, datetime)
            # print("CALC INDEX:", start_date, ", ", calculateDate, ", ", floor((calculateDate-start_date)/interval))
            return floor((calculateDate-start_date)/interval)

        for freeObject in self.getFreeInterval(start_date, end_date):
            for freeRange in Free.timeGenerator(freeObject.start_date, freeObject.end_date, interval):
                freeArray[calculateIndex(start_date, interval, freeRange)] = 1

        return freeArray
    def getFreeArrayProfiles(self, start_date, end_date, interval=timedelta(minutes=30)):
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        assert isinstance(interval, timedelta)
        start_date = Free.makeTimezoneAware(start_date)
        end_date = Free.makeTimezoneAware(end_date)
        freeArray = []
        for x in Free.timeGenerator(Free.makeTimezoneAware(start_date), Free.makeTimezoneAware(end_date), interval):
            freeArray.append(0)
        # print("ARRAY LENGTH:", len(freeArray))
        def calculateIndex(start_date, interval, calculateDate):
            assert isinstance(start_date, datetime)
            assert isinstance(interval, timedelta)
            assert isinstance(calculateDate, datetime)
            # print("CALC INDEX:", start_date, ", ", calculateDate, ", ", floor((calculateDate-start_date)/interval))
            return floor((calculateDate-start_date)/interval)

        for freeObject in self.getFreeInterval(start_date, end_date):
            for freeRange in Free.timeGenerator(freeObject.start_date, freeObject.end_date, interval):
                freeArray[calculateIndex(start_date, interval, freeRange)] = self

        return freeArray
            
    def __str__(self):
        return str(self.user)

class Event(models.Model):
    code_name = models.SlugField(unique=True, max_length=50)
    title = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    length = models.PositiveSmallIntegerField(default=1)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def attendeesMap(self):
        attendeeMap = {}
        for x in self.attendees:
            attendeeMap[x.id] = x
        return attendeeMap

    @staticmethod
    def deleteOutOfDate():
        Event.objects.filter(end_date__lte=Free.makeTimezoneAware(datetime.now())).delete()

    @staticmethod
    def date_to_js(givenDate):
        assert isinstance(givenDate, datetime)
        return datetime.strftime(givenDate, "%d %b %Y %H:%M:%S")

    def start_date_js(self):
        return Event.date_to_js(self.start_date)

    def end_date_js(self):
        return Event.date_to_js(self.end_date)


    def attendeesFormatted(self):
        attending = self.attendees
        if attending.count() == 0:
            return ""
        if attending.count() == 1:
            return attending.first()
        return ", ".join([str(x) for x in attending])

    @property
    def attendees(self):
        return self.profile_set.all()

    #numbers
    def getOverlapHeatMap(self, start_date=None, end_date=None):
        heat = []
        if not start_date:
            start_date = self.start_date
        if not end_date:
            end_date = self.end_date

        for day in self.getOverlapProfiles(start_date, end_date):
            heat.append(len(day))
        return heat

    def getOverlapProfiles(self, start_date=None, end_date=None, **kwargs):
        all_overlaps = []
        to_json = kwargs.get("json", False)
        if not start_date:
            start_date = self.start_date
        if not end_date:
            end_date = self.end_date

        for profile in self.attendees:
            i = 0
            for free in profile.getFreeArray(start_date, end_date):
                if to_json:
                    to_append = profile.user.username
                else:
                    to_append = profile
                if free:
                    try:
                        all_overlaps[i].append(to_append)
                    except:
                        all_overlaps.append([to_append,])
                else:
                    try:
                        all_overlaps[i]
                    except:
                        all_overlaps.append([])
                i += 1

        return all_overlaps

    def getOptimalTimes(self):
        def getOptimalTimesInner(consecutivePeople, profilesArray):
            bestTimes = []
            i = 0
            freeLength = 0
            startFree = None
            for time in Free.timeGenerator(self.start_date, self.end_date, timedelta(minutes=30)):
                peopleFree = len(profilesArray[i])
                if(peopleFree >= consecutivePeople):
                    if freeLength == 0:
                        startFree = time
                    if freeLength >= self.length:
                        bestTimes.append((startFree, time))
                        startFree += timedelta(minutes=30)
                    else:
                        freeLength += .5
                else:
                    if freeLength >= self.length:
                        bestTimes.append((startFree, time))
                    freeLength = 0
                i += 1
            return bestTimes

        profilesArray = self.getOverlapProfiles()
        if not profilesArray:
            return [None]
        
        for consecutivePeople in range(self.attendees.count()+1, 1, -1):
            result = getOptimalTimesInner(consecutivePeople, profilesArray)
            if result:
                return result
        return []

    class Meta:
        ordering = ("-start_date", "-end_date")

    def __str__(self):
        return self.title + " at " + str(self.start_date) + " to " + str(self.end_date) + " created by " + str(self.creator)


class Free(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    @staticmethod
    def deleteOutOfDate():
        Free.objects.filter(end_date__lte=datetime.now()).delete()

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

    
        

            
