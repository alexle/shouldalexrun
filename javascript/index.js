function AddIconToId( ID, IconName )
{
   var skycons = new Skycons();

   switch (IconName)
   {
      case "clear-day":
         skycons.add(ID, Skycons.CLEAR_DAY);
         break;

      case "clear-night":
         skycons.add(ID, Skycons.CLEAR_NIGHT);
         break;

      case "partly-cloudy-day":
         skycons.add(ID, Skycons.PARTLY_CLOUDY_DAY);
         break;

      case "partly-cloudy-night":
         skycons.add(ID, Skycons.PARTLY_CLOUDY_NIGHT);
         break;

      case "cloudy":
         skycons.add(ID, Skycons.CLOUDY);
         break;

      case "rain":
         skycons.add(ID, Skycons.RAIN);
         break;

      case "sleet":
         skycons.add(ID, Skycons.SLEET);
         break;

      case "snow":
         skycons.add(ID, Skycons.SNOW);
         break;

      case "wind":
         skycons.add(ID, Skycons.WIND);
         break;

      case "fog":
         skycons.add(ID, Skycons.WIFOGND);
         break;
   }

   skycons.play();
}

function LoadSkyCon()
{
   //var IconIds = ["curr", "day1", "day2", "day3", "day4", "day5"]
   var IconIds = ["curr", "hour1", "hour2", "hour3", "hour4", "hour5", "hour6",
                  "hour7", "hour8", "hour9", "hour10", "hour11", "hour12"]

   for (i = 0; i < IconIds.length; i++)
   {
      AddIconToId( IconIds[i], document.getElementById(IconIds[i]).className )
   }
}

