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
                  "hour7", "hour8", "hour9", "hour10", "hour11", "hour12",
                  "day1", "day2", "day3", "day4", "day5"]

   for (i = 0; i < IconIds.length; i++)
   {
      AddIconToId( IconIds[i], document.getElementById(IconIds[i]).className )
   }
}

$(document).ready(function() {
 
 //When page loads...
 $(".tab_content").hide(); //Hide all content
 $("ul.tabs li:first").addClass("active").show(); //Activate first tab
 $(".tab_content:first").show(); //Show first tab content
 
 //On Click Event
 $("ul.tabs li").click(function() {
 
  $("ul.tabs li").removeClass("active"); //Remove any "active" class
  $(this).addClass("active"); //Add "active" class to selected tab
  $(".tab_content").hide(); //Hide all tab content
 
  var activeTab = $(this).find("a").attr("href"); //Find the href attribute value to identify the active tab + content
  $(activeTab).fadeIn(); //Fade in the active ID content
  return false;
 });
 
});

