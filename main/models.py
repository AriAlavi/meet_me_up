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
        print("ARRAY LENGTH:", len(freeArray))
        def calculateIndex(start_date, interval, calculateDate):
            assert isinstance(start_date, datetime)
            assert isinstance(interval, timedelta)
            assert isinstance(calculateDate, datetime)
            print("CALC INDEX:", start_date, ", ", calculateDate, ", ", floor((calculateDate-start_date)/interval))
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
    def getOverlapHeatMap(self):
        heat = []
        for day in self.getOverlapProfiles():
            heat.append(len(day))
        return heat
#         super_arr = []
#         final_arr = []
#         new_arr = []
#         event_start_date = self.start_date
#         event_end_date = self.end_date
#         #Queryset of profiles
#         profiles = self.profile_set.all()

#         for x in profiles:
#             #Get free time intervals of profile
#             arr = x.getFreeArray(event_start_date,event_end_date)
#             super_arr.append(arr)
#         #create empty array to add everything in
    
#         for i in range(len(super_arr[0])):
#             final_arr.append(0)
#         #add all the arrays together
#         for a in super_arr:
#             for b in a:
#                 final_arr[b] = final_arr[b] + super_arr[a][b]
# #Gives fractional map
# #        #create array of fractions to represent what percent of people are free at any time
# #        for i in final_arr:
# #            new_arr.append(final_arr[i]/len(super_arr))
# #        return new_arr

# #Gives whole number map
#         return final_arr
    
    #profiles
    # def getOverlapProfiles(self):
    #     final_arr = []
    #     super_arr = []
    #     event_start_date = self.start_date
    #     event_end_date = self.end_date
    #     #Queryset of profiles
    #     profiles = self.profile_set.all()
        
    #     for x in profiles:
    #         #Get free time intervals of profile
    #         arr = x.getFreeArrayProfiles(event_start_date,event_end_date)
    #         super_arr.append(arr)
    #     #add all the arrays together
    #     for a in super_arr:
    #         arr = []
    #         for b in a:
    #             if super_arr[a][b] is not 0:
    #                 arr.append(super_arr[a][b])
    #         final_arr.append(arr)
    #     return final_arr
    def getOverlapProfiles(self):
        all_overlaps = []

        for profile in self.attendees:
            i = 0
            for free in profile.getFreeArray(self.start_date, self.end_date):
                if free:
                    try:
                        all_overlaps[i].append(profile)
                    except:
                        all_overlaps.append([profile,])
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
                    if freeLength >= self.length:
                        bestTimes.append((startFree, time))
                        startFree += timedelta(minutes=30)
                    else:
                        freeLength += .5
                else:
                    freeLength = 0
                    startFree = time
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

    
        

            
