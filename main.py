import os, sys
import webapp2, jinja2, logging, json, datetime
from google.appengine.api import urlfetch

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Get secret and consumer key from data file
FILE = open('templates/data.txt', 'r')
FORECAST_KEY = FILE.readline().strip()
BING_KEY = FILE.readline().strip()

CompassDirection = [ 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW' ]

class CurrentlyData:
   icon = ''
   temperature = ''
   summary = ''
   wind_speed = ''
   wind_bearing = ''
   time = '' 
   precip_intensity = '' 
   precip_prob = ''
   humidity = ''
   cloud_cover = ''

class DayEntry:
   icon = ''
   summary = ''
   time = ''
   temp_min = ''
   temp_max = ''
   precip_prob = ''

class Verdict:
   status = ''
   msg = ''

DailyData = []

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
   CurrentData.wind_speed = json_data['currently']['windSpeed']
   CurrentData.wind_bearing = CompassDirection[ (int(json_data['currently']['windBearing'] + 180 + 22) % 360) / 45 ]
   CurrentData.precip_prob = int(round(json_data['currently']['precipProbability'] * 100))
   CurrentData.precip_intensity = json_data['currently']['precipIntensity']
   CurrentData.humidity = int(round(json_data['currently']['humidity'] * 100))
   CurrentData.cloud_cover = int(round(json_data['currently']['cloudCover'] * 100))
   CurrentData.time = datetime.datetime.fromtimestamp(int(json_data['currently']['time'])).strftime('%a %m-%d %I:%M %p')

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
   
   return CurrentData, DailyData

def ShouldAlexRun( CurrentData ):
   V = Verdict()
   if CurrentData.temperature < 74:
      V.status = True
      V.msg = 'YES'
   else:
      V.status = False 
      V.msg = 'NO, too hot'

   return V

class MainHandler(webapp2.RequestHandler):
   def get(self):

      CurrentData, DailyData = GetWeatherData(None, None)

      Verdict = ShouldAlexRun( CurrentData )

      template_values = {
         'CurrentData': CurrentData,
         'DailyData': DailyData,
         'Verdict': Verdict,
      }
      
      template = jinja_environment.get_template('index.html')
      self.response.out.write( template.render( template_values ) )

app = webapp2.WSGIApplication([
                  ('/', MainHandler),
               ], debug=True)
