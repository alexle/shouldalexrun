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
   var IconIds = ["curr", "hour1", "hour2", "hour3", "hour4", "hour5", "hour6",
                  "hour7", "hour8", "hour9", "hour10", "hour11", "hour12",
                  "hour13", "hour14", "hour15", "hour16", "hour17", "hour18",
                  "hour19", "hour20", "hour21", "hour22", "hour23", "hour24",
                  "day1", "day2", "day3", "day4", "day5"]

   for (i = 0; i < IconIds.length; i++)
   {
      AddIconToId( IconIds[i], document.getElementById(IconIds[i]).className )
   }
}

$(document).ready(function() {
   $(".tab_content").hide();
   $("ul.tabs li:first").addClass("active").show();
   $(".tab_content:first").show();
 
   $("ul.tabs li").click(function() {
      $("ul.tabs li").removeClass("active");
      $(this).addClass("active");
      $(".tab_content").hide();
   
      var activeTab = $(this).find("a").attr("href");
      $(activeTab).fadeIn();
      return false;
   });
});

