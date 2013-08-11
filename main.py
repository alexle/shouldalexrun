import os, sys
import webapp2, jinja2, logging, json
from google.appengine.api import urlfetch

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Get secret and consumer key from data file
FILE = open('templates/data.txt', 'r')
CONSUMER_KEY = FILE.readline().strip()

class CurrentlyData:
   icon = ''
   temperature = ''
   summary = ''
   wind_speed = ''
   time = '' 
   precip_intensity = '' 
   precip_prob = ''
   humidity = ''

def GetWeatherData( latitude, longitude ):
   Data = CurrentlyData()
   url = "https://api.forecast.io/forecast/"
   latitude = '39.932318'
   longitude = '-104.985907'

   full_url = url + CONSUMER_KEY + '/' + latitude + ',' + longitude

   data = urlfetch.fetch(full_url, deadline=10).content
   json_data = json.loads(data)

   Data.icon = json_data['currently']['icon']
   Data.temperature = json_data['currently']['temperature']
   Data.summary = json_data['currently']['summary']
   Data.wind_speed = json_data['currently']['windSpeed']
   Data.precip_prob = json_data['currently']['precipProbability']
   Data.precip_intensity = json_data['currently']['precipIntensity']
   Data.time = json_data['currently']['time']
   Data.humidity = json_data['currently']['humidity']

   return Data 
      

class MainHandler(webapp2.RequestHandler):
   def get(self):

      CurrentData = GetWeatherData(None, None)

      template_values = {
         'CurrentData': CurrentData,
      }
      
      template = jinja_environment.get_template('index.html')
      self.response.out.write( template.render( template_values ) )

app = webapp2.WSGIApplication([
                  ('/', MainHandler),
               ], debug=True)
