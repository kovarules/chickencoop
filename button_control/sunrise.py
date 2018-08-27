import datetime
from astral import Astral
from datetime import date


city_name = 'Brussels'

a = Astral()
a.solar_depression = 'civil'
city = a[city_name]
timezone = city.timezone

print('Information for %s/%s\n' % (city_name, city.region))
print('Timezone: %s' % timezone)
print('Latitude: %.02f; Longitude: %.02f\n' % (city.latitude, city.longitude))

sun = city.sun(date=datetime.date(2009, 4, 22), local=True)
print('Dawn:    %s' % str(sun['dawn']))
print('Sunrise: %s' % str(sun['sunrise']))
print('Noon:    %s' % str(sun['noon']))
print('Sunset:  %s' % str(sun['sunset']))
print('Dusk:    %s' % str(sun['dusk']))

today = date.today()
if currentDay != today:
	#there is a bright new day we need to calculate the sun for
	currentDay = today
	sun = city.sun(date=datetime.date(2009, 4, 22), local=True)
	print('Dawn:    %s' % str(sun['dawn']))
	print('Sunrise: %s' % str(sun['sunrise']))
	print('Noon:    %s' % str(sun['noon']))
	print('Sunset:  %s' % str(sun['sunset']))
	print('Dusk:    %s' % str(sun['dusk']))
	closingTime = sun['sunset'].time()
	openingTime = sun['sunrise'].time()

	
# check if we are supposed to open or close the chickencoop
currentTime = datetime.datetime.now().time()
if openingTime < currentTime:
	#open door
else if closingTime < currentTime:
	#close door