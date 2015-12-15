import os, sys
import webapp2, jinja2, logging, json
from google.appengine.api import urlfetch

from datetime import datetime, timedelta

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

DEFAULT_ZIPCODE = '80241'

# Constants
class Constants:
   DayEntries = 5
   HourEntries = 24
   MaxTemp = 78
   MinTemp = 32
   MaxWind = 12
   MaxRain = 40
   CloudAdjustPercent = 10

# Get secret and consumer key from data file
FILE = open('templates/data.txt', 'r')
FORECAST_KEY = FILE.readline().strip()
BING_KEY = FILE.readline().strip()

CompassDirection = [ 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW' ]

class CurrentlyData:
   def __init__(self):
      self.time = ''
      self.icon = ''
      self.temperature = ''
      self.summary = ''
      self.precip_prob = ''
      self.precip_intensity = ''
      self.wind_speed = ''
      self.wind_bearing = ''
      self.cloud_cover = ''
      self.status = ''
      self.msg = ''

class DayEntry:
   icon = ''
   summary = ''
   time = ''
   temp_min = ''
   temp_max = ''
   precip_prob = ''
   wind_speed = ''

class HourlyEntry:
   def __init__(self):
      self.time = ''
      self.icon = ''
      self.temperature = ''
      self.summary = ''
      self.precip_prob = ''
      self.precip_intensity = ''
      self.wind_speed = ''
      self.wind_bearing = ''
      self.cloud_cover = ''
      self.status = ''
      self.msg = ''

class GeocodeInfo:
   latitude = ''
   longitude = ''
   form_addr = ''

class InputLocation:
   city = ''
   state = ''
   country = ''
   zipcode = ''

def GetGeocodeData( loc ):
   url = "http://dev.virtualearth.net/REST/v1/Locations?"

   loc.country = ''
   loc.zipcode = ''

   s = []
   s.append(url)
   s.append("CountryRegion=" + loc.country)
   s.append("&adminDistrict=" + loc.state)
   s.append("&locality=" + loc.city)
   s.append("&postalCode=" + loc.zipcode)
   s.append("&addressLine=" + "13001%Grant%Cir")
   s.append("&key=" + BING_KEY)
   full_url = ''.join(s)

   data = urlfetch.fetch(full_url, deadline=10).content
   json_data = json.loads(data)

   return json_data

def ParseGeocodeData( json ):

   # Fill out geocode structure from Bing results
   geo = GeocodeInfo()

   geo.latitude = str(json['resourceSets'][0]['resources'][0]['point']['coordinates'][0])
   geo.longitude = str(json['resourceSets'][0]['resources'][0]['point']['coordinates'][1])
   geo.format_addr = json['resourceSets'][0]['resources'][0]['address']['formattedAddress']
   logging.info('+++++++')
   logging.info(json['resourceSets'][0]['resources'][0]['address'])

   logging.info(geo.latitude)
   logging.info(geo.longitude)

   return geo


def ShouldAlexRun( entry ):

   # Allow cloud adjustment if temperature is greater than max
   if entry.temperature > Constants.MaxTemp:
      mod_temp = entry.temperature - (entry.cloud_cover / Constants.CloudAdjustPercent)
   else:
      mod_temp = entry.temperature

   if ( mod_temp <= Constants.MaxTemp and
        mod_temp >= Constants.MinTemp and
        entry.precip_prob < Constants.MaxRain and
        entry.wind_speed < Constants.MaxWind ):

      entry.status = True
      entry.msg = 'YES'

   else:
      entry.status = False
      entry.msg = 'NO'

def GetWeatherData( geo ):
   url = "https://api.forecast.io/forecast/"

   full_url = url + FORECAST_KEY + '/' + geo.latitude + ',' + geo.longitude + '?exclude=minutely,alerts,flags'

   data = urlfetch.fetch(full_url, deadline=10).content
   json_data = json.loads(data)

   return json_data

# Parse Currently structure from json
def ParseCurrently(json):
   curr_data = CurrentlyData()

   curr_data.icon = json['currently']['icon']
   curr_data.temperature = int(round(json['currently']['apparentTemperature']))
   curr_data.summary = json['currently']['summary']
   curr_data.wind_speed = int(round(json['currently']['windSpeed']))
   curr_data.precip_prob = int(round(json['currently']['precipProbability'] * 100))
   curr_data.precip_intensity = json['currently']['precipIntensity']
   curr_data.cloud_cover = int(round(json['currently']['cloudCover'] * 100))

   try:
      curr_data.wind_bearing = CompassDirection[ (int(json['currently']['windBearing'] + 180 + 22) % 360) / 45 ]
   except:
      curr_data.wind_bearing = 0

   loc_datetime = datetime.fromtimestamp(json['currently']['time']) + timedelta(hours=int(json['offset']))
   curr_data.time = loc_datetime.strftime('%I:%M %p').lstrip('0').lower()

   ShouldAlexRun( curr_data )

   return curr_data

# Parse Daily structure from json
def ParseDaily(json):
   DailyData = []

   for i in range(Constants.DayEntries):
      day_entry = DayEntry()

      day_entry.icon = json['daily']['data'][i]['icon']
      day_entry.temp_max = int(round(json['daily']['data'][i]['temperatureMax']))
      day_entry.temp_min = int(round(json['daily']['data'][i]['temperatureMin']))
      day_entry.precip_prob= int(round(json['daily']['data'][i]['precipProbability'] * 100))
      day_entry.wind_speed = int(round(json['currently']['windSpeed']))
      day_entry.summary = json['daily']['data'][i]['summary']

      loc_datetime = datetime.fromtimestamp(json['daily']['data'][i]['time']) + timedelta(hours=int(json['offset']))
      day_entry.time = loc_datetime.strftime('%a').lstrip('0')

      DailyData.append(day_entry)

   return DailyData

# Parse Hourly structure from json
def ParseHourly(json):
   HourlyData = []

   for i in range(Constants.HourEntries):
      hour_entry = HourlyEntry()

      hour_entry.icon = json['hourly']['data'][i]['icon']
      hour_entry.summary = json['hourly']['data'][i]['summary']
      hour_entry.temperature = int(round(json['hourly']['data'][i]['apparentTemperature']))
      hour_entry.precip_prob= int(round(json['hourly']['data'][i]['precipProbability'] * 100))
      hour_entry.wind_speed = int(round(json['hourly']['data'][i]['windSpeed']))
      hour_entry.cloud_cover = int(round(json['hourly']['data'][i]['cloudCover'] * 100))

      loc_datetime = datetime.fromtimestamp(json['hourly']['data'][i]['time']) + timedelta(hours=int(json['offset']))
      hour_entry.time = loc_datetime.strftime('%I%p').lstrip('0').lower()

      try:
         hour_entry.wind_bearing = CompassDirection[ (int(json['hourly']['data'][i]['windBearing'] + 180 + 22) % 360) / 45 ]
      except:
         hour_entry.wind_bearing = 0

      HourlyData.append(hour_entry)

      ShouldAlexRun( hour_entry )

   return HourlyData

class MainHandler(webapp2.RequestHandler):
   def get(self):

      loc = InputLocation()
      #loc.zipcode = self.request.get('zipcode')
      loc.city = self.request.get('input_city')
      loc.state = self.request.get('input_state')

      if loc.zipcode == '':
         loc.zipcode = DEFAULT_ZIPCODE
      if loc.city == '':
         loc.city = 'Thornton'
      if loc.state == '':
         loc.state = 'CO'

      g_json = GetGeocodeData(loc)

      GeocodeData = ParseGeocodeData(g_json)

      json = GetWeatherData(GeocodeData)

      CurrentData = ParseCurrently(json)
      DailyData = ParseDaily(json)
      HourlyData = ParseHourly(json)

      template_values = {
         'CurrentData': CurrentData,
         'DailyData': DailyData,
         'HourlyData': HourlyData,
         'GeocodeData': GeocodeData,
         'Constants': Constants,
      }

      template = jinja_environment.get_template('index.html')
      self.response.out.write( template.render( template_values ) )

app = webapp2.WSGIApplication([
                  ('/', MainHandler),
               ], debug=True)
