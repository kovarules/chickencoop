import time
from tzlocal import get_localzone
from astral import Astral
from datetime import date, datetime, timedelta



class TimeCheck:

    def __init__(self, cityname):
        a = Astral()
        a.solar_depression = 'civil'
        self.city = a[cityname]
        self.times = None
        self.currentDay = None
        self.slowPokeRetryTime = timedelta(minutes=30)
        self.slowPokeOpenTime = timedelta(minutes=5)
        self.openingTime = None
        self.closingTime = None
        self.slowPokeReopenTime = None
        self.finalClosingTime = None

        print('Information for %s/%s' % (cityname, self.city.region))
        print('Timezone: %s' % self.city.timezone)
        print('Latitude: %.02f; Longitude: %.02f\n' % (self.city.latitude, self.city.longitude))

    def PrintDuskTillDawn(self, times):
        print('Dawn:    %s' % str(times['dawn']))
        print('Sunrise: %s' % str(times['sunrise']))
        print('Noon:    %s' % str(times['noon']))
        print('Sunset:  %s' % str(times['sunset']))
        print('Dusk:    %s' % str(times['dusk']))

    def Run(self):
        today = date.today()
        # triggerDoor = False
        if self.currentDay != today:
            # there is a bright new day we need to calculate the sun for
            print('currentDay was %s' % str(self.currentDay))
            print('today is %s' % str(today))
            self.currentDay = today
            sun = self.city.sun(self.currentDay, local=True)
            # self.PrintDuskTillDawn(sun)

            is_dst = time.daylight and time.localtime().tm_isdst > 0
            if is_dst:
                # we're in daylight savings time, the sunrise is not corrected for dst
                dst_offset = timedelta(hours=-1)
            else:
                dst_offset = timedelta(hours=0)

            self.openingTime = sun['sunrise'].replace(tzinfo=get_localzone()) + dst_offset
            self.closingTime = sun['sunset'].replace(tzinfo=get_localzone()) + dst_offset
            print ('opening %s' % self.openingTime)
            print ('closing %s' % self.closingTime)
            self.slowPokeReopenTime = self.closingTime + self.slowPokeRetryTime
            self.finalClosingTime = self.slowPokeReopenTime + self.slowPokeOpenTime

        # Check what should happen with the door according to the time
        now = datetime.now().replace(tzinfo=get_localzone())

        print('now is %s' % str(now))
        # check if we are supposed to open or close the chickencoop
        if now < self.openingTime:
            # door should be closed unless manual action forced it open
            print("door closed")
        elif self.openingTime <= now < self.closingTime:
            # door should be open
            print("door opened")
        elif self.closingTime <= now < self.slowPokeReopenTime:
            # door should be closed
            print("door closed")
        elif self.slowPokeReopenTime <= now < self.finalClosingTime:
            # door should be open
            print("door opened slowpoke")
        elif self.finalClosingTime <= now:
            # door should be closed
            print("door finalclosed")
        else:
            print("Error time comparison")


t = TimeCheck('Brussels')

t.Run()
