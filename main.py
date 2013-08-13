import os, sys
import webapp2, jinja2, logging, json, datetime
from google.appengine.api import urlfetch

from pytz import timezone
import pytz

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Get secret and consumer key from data file
FILE = open('templates/data.txt', 'r')
FORECAST_KEY = FILE.readline().strip()
BING_KEY = FILE.readline().strip()

CompassDirection = [ 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW' ]

class CurrentlyData:
   time = '' 
   icon = ''
   temperature = ''
   summary = ''
   wind_speed = ''
   precip_prob = ''
   precip_intensity = '' 
   wind_bearing = ''
   humidity = ''
   cloud_cover = ''
   status = ''
   msg = ''

class DayEntry:
   icon = ''
   summary = ''
   time = ''
   temp_min = ''
   temp_max = ''
   precip_prob = ''

class HourlyEntry:
   time = ''
   icon = ''
   temperature = ''
   summary = ''
   precip_prob = ''
   wind_speed = ''
   wind_bearing = ''
   cloud_cover = ''
   status = ''
   msg = ''

DailyData = []
HourlyData = []

def CalcTimeZone( naive_date, time_zone ):
   tz = timezone( time_zone )

   dt = tz.localize( naive_date)


def ShouldAlexRun( Entry ):
   if Entry.temperature < 73 and Entry.wind_speed < 10:
      Entry.status = True
      Entry.msg = 'YES'
   else:
      Entry.status = False 
      Entry.msg = 'NO'

def GetWeatherData( latitude, longitude ):
   CurrentData = CurrentlyData()
   url = "https://api.forecast.io/forecast/"
   latitude = '39.932318'
   longitude = '-104.985907'

   full_url = url + FORECAST_KEY + '/' + latitude + ',' + longitude + '?exclude=alerts,flags'

   data = urlfetch.fetch(full_url, deadline=10).content
   json_data = json.loads(data)

   # Parse Currently structure from json
   CurrentData.icon = json_data['currently']['icon']
   CurrentData.temperature = int(round(json_data['currently']['temperature']))
   CurrentData.summary = json_data['currently']['summary']
   CurrentData.wind_speed = round(json_data['currently']['windSpeed'] * 10) / 10
   CurrentData.wind_bearing = CompassDirection[ (int(json_data['currently']['windBearing'] + 180 + 22) % 360) / 45 ]
   CurrentData.precip_prob = int(round(json_data['currently']['precipProbability'] * 100))
   CurrentData.precip_intensity = json_data['currently']['precipIntensity']
   CurrentData.humidity = int(round(json_data['currently']['humidity'] * 100))
   CurrentData.cloud_cover = int(round(json_data['currently']['cloudCover'] * 100))
   CurrentData.time = datetime.datetime.fromtimestamp(int(json_data['currently']['time'])).strftime('%a %m-%d %I:%M %p')

   ShouldAlexRun( CurrentData )

   # Parse Daily structure from json
   for i in range(5):
      day_entry = DayEntry()

      day_entry.time = datetime.datetime.fromtimestamp(int(json_data['daily']['data'][i]['time'])).strftime('%a')
      day_entry.temp_min = int(round(json_data['daily']['data'][i]['temperatureMin']))
      day_entry.temp_max = int(round(json_data['daily']['data'][i]['temperatureMax']))
      day_entry.precip_prob= int(round(json_data['daily']['data'][i]['precipProbability'] * 100))
      day_entry.icon = json_data['daily']['data'][i]['icon']
      day_entry.summary = json_data['daily']['data'][i]['summary']

      DailyData.append(day_entry)
   
   # Parse Hourly structure from json
   for i in range(12):
      hour_entry = HourlyEntry()

      hour_entry.icon = json_data['hourly']['data'][i]['icon']
      hour_entry.summary = json_data['hourly']['data'][i]['summary']
      hour_entry.time = datetime.datetime.fromtimestamp(int(json_data['hourly']['data'][i]['time'])).strftime('%I %p')
      hour_entry.temperature = int(round(json_data['hourly']['data'][i]['temperature']))
      hour_entry.precip_prob= int(round(json_data['hourly']['data'][i]['precipProbability'] * 100))
      hour_entry.wind_speed = round(json_data['hourly']['data'][i]['windSpeed'] * 10) / 10
      hour_entry.wind_bearing = CompassDirection[ (int(json_data['hourly']['data'][i]['windBearing'] + 180 + 22) % 360) / 45 ]
      hour_entry.cloud_cover = int(round(json_data['hourly']['data'][i]['cloudCover'] * 100))

      HourlyData.append(hour_entry)

      ShouldAlexRun( hour_entry )

   return CurrentData, DailyData, HourlyData

class MainHandler(webapp2.RequestHandler):
   def get(self):

      CurrentData, DailyData, HourlyData = GetWeatherData(None, None)

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
