import logging

import time
from tzlocal import get_localzone
from astral import Astral
from datetime import date, datetime, timedelta

logging.basicConfig(level=logging.DEBUG)

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
        self.tzinfo = get_localzone()
        print ("timezone %s" % self.tzinfo)
        print('Information for %s/%s' % (cityname, self.city.region))
        print('Timezone: %s' % self.city.timezone)
        # print('Latitude: %.02f; Longitude: %.02f\n' % (self.city.latitude, self.city.longitude))

    @staticmethod
    def print_dusk_till_dawn(times):
        print('Dawn:    %s' % str(times['dawn']))
        print('Sunrise: %s' % str(times['sunrise']))
        print('Noon:    %s' % str(times['noon']))
        print('Sunset:  %s' % str(times['sunset']))
        print('Dusk:    %s' % str(times['dusk']))

    def run(self):
        today = date.today()
        # triggerDoor = False
        if self.currentDay != today:
            # there is a bright new day we need to calculate the sun for
            print('currentDay was %s' % str(self.currentDay))
            print('today is %s' % str(today))
            self.currentDay = today
            sun = self.city.sun(self.currentDay, local=True)
            # self.print_dusk_till_dawn(sun)

            is_dst = time.daylight and time.localtime().tm_isdst > 0
            if is_dst:
                # we're in daylight savings time, the sunrise is not corrected for dst
                dst_offset = timedelta(hours=-1)
            else:
                dst_offset = timedelta(hours=0)
            self.openingTime = sun['sunrise'].replace(tzinfo = get_localzone()) + dst_offset
            self.closingTime = sun['dusk'].replace(tzinfo = get_localzone()) + timedelta(minutes=20) + dst_offset
            print ('opening %s' % self.openingTime)
            print ('closing %s' % self.closingTime)
            self.slowPokeReopenTime = self.closingTime + self.slowPokeRetryTime
            self.finalClosingTime = self.slowPokeReopenTime + self.slowPokeOpenTime

        # Check what should happen with the door according to the time
        now = datetime.now().replace(tzinfo = get_localzone())
        print('now is %s' % str(now))

        # check if we are supposed to open or close the chickencoop
        if now < self.openingTime:
            # door should be closed unless manual action forced it open
            print("door closed")
            return False
        elif self.openingTime <= now < self.closingTime:
            # door should be open
            print("door opened")
            return True
        elif self.closingTime <= now < self.slowPokeReopenTime:
            # door should be closed
            print("door closed")
            return False
        elif self.slowPokeReopenTime <= now < self.finalClosingTime:
            # door should be open
            print("door opened slowpoke")
            return True
        elif self.finalClosingTime <= now:
            # door should be closed
            print("door final closed")
            return False
        else:
            print("Error time comparison")
            return False


def main():
    t = TimeCheck('Brussels')
    t.run()


if __name__ == "__main__":
    main()
