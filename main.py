import os, sys
import webapp2, jinja2, logging, json
from google.appengine.api import urlfetch

from datetime import datetime, timedelta

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#Contants
DAY_ENTRIES = 5
HOUR_ENTRIES = 12
MAX_TEMP = 74
MIN_TEMP = 40 
MAX_WIND = 10
CLOUD_ADJ_PERCENT = 12
MAX_RAIN = 50

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
      location = ''

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


def ShouldAlexRun( entry ):
   mod_temp = entry.temperature - (entry.cloud_cover / CLOUD_ADJ_PERCENT)

   if (mod_temp <= MAX_TEMP and mod_temp >= MIN_TEMP and
       entry.precip_prob < MAX_RAIN and entry.wind_speed < MAX_WIND ):
      entry.status = True
      entry.msg = 'YES'
   else:
      entry.status = False 
      entry.msg = 'NO'

def GetWeatherData( latitude, longitude ):
   url = "https://api.forecast.io/forecast/"
   latitude = '39.932318'
   longitude = '-104.985907'

   full_url = url + FORECAST_KEY + '/' + latitude + ',' + longitude + '?exclude=alerts,flags'

   data = urlfetch.fetch(full_url, deadline=10).content
   json_data = json.loads(data)

   return json_data

# Parse Currently structure from json
def ParseCurrently(json):
   curr_data = CurrentlyData()

   curr_data.icon = json['currently']['icon']
   curr_data.temperature = int(round(json['currently']['temperature']))
   curr_data.summary = json['currently']['summary']
   curr_data.wind_speed = int(round(json['currently']['windSpeed']))
   curr_data.precip_prob = int(round(json['currently']['precipProbability'] * 100))
   curr_data.precip_intensity = json['currently']['precipIntensity']
   curr_data.cloud_cover = int(round(json['currently']['cloudCover'] * 100))
   curr_data.location = 'Thornton, CO'

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

   for i in range(DAY_ENTRIES):
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

   for i in range(HOUR_ENTRIES):
      hour_entry = HourlyEntry()

      hour_entry.icon = json['hourly']['data'][i]['icon']
      hour_entry.summary = json['hourly']['data'][i]['summary']
      hour_entry.temperature = int(round(json['hourly']['data'][i]['temperature']))
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

      json = GetWeatherData(None, None)

      CurrentData = ParseCurrently(json)
      DailyData = ParseDaily(json)
      HourlyData = ParseHourly(json)

      template_values = {
         'CurrentData': CurrentData,
         'DailyData': DailyData,
         'HourlyData': HourlyData,
      }
      
      template = jinja_environment.get_template('index.html')
      self.response.out.write( template.render( template_values ) )

app = webapp2.WSGIApplication([
                  ('/', MainHandler),
               ], debug=True)
