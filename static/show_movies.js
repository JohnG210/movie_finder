// Vars

// Functions
function display_movie_list(movies_list){
    $.each(movies_list['Title'], function( index) {
        let correct_idx = parseInt(movies_list["Rank"][index])-1
        $("#pop-movie-cont").append('<div class="row" id="movie-container">' + 
        '<div class="col-md-1 rank-col">' + movies_list["Rank"][index] + '</div>' +
        '<div class="col-md-5 names-col"><a href="/movie/'+ correct_idx.toString() + '">' + movies_list["Title"][index] + '</a></div>' +
        '<div class="col-md-2 rate-col">' + movies_list["Certificate"][index] + '</div>' +
        '<div class="col-md-2 watched-col" id="watched-col-' + index + '">' + '' + '</div>' + 
        '<div class="col-md-2 ws">' + '' + '</div>' +
        '</div>')
        let section = '#watched-col-' + index
        if (movies_list["users_seen"][index].includes('john'))
        {
            $(section).append('<button type="button" class="btn btn-primary btn-circle btn-xl">J</button>')
        }
        if (movies_list["users_seen"][index].includes('violet'))
        {
            $(section).append('<button type="button" class="btn btn-secondary btn-circle btn-xl">V</button>')
        }
        if (movies_list["users_seen"][index].includes('test'))
        {
            $(section).append('<button type="button" class="btn btn-secondary btn-circle btn-xl">T</button>')
        }
    })
}

function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  // Close the dropdown if the user clicks outside of it
  window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }

// Change the name of the sales person
function change_guest() {
  let guestname = $("#guest-name").val()
  $.ajax({
      type: "POST",
      url: "change_guest",                
      dataType : "json",
      contentType: "application/json; charset=utf-8",
      data : JSON.stringify(guestname),
      success: function(result){
          console.log('changed guest to ' + guestname)
          location.reload()
          // $("#new_name").val("")
      },
      error: function(request, status, error){
          console.log("Error");
          console.log(request)
          console.log(status)
          console.log(error)
      }
  });
}

// Change the name of the sales person
function change_user() {
  let user = $("#enter-user").val()
  $.ajax({
      type: "POST",
      url: "change_user",                
      dataType : "json",
      contentType: "application/json; charset=utf-8",
      data : JSON.stringify(user),
      success: function(result){
          console.log('changed user to ' + user)
          location.reload()
          // $("#new_name").val("")
      },
      error: function(request, status, error){
          console.log("Error");
          console.log(request)
          console.log(status)
          console.log(error)
      }
  });
}

// Runtime code
$(document).ready(function()
{
    // FIRST SETUP
    // initalize the movies
    display_movie_list(movies_list)
    $( "#change-guest-button" ).click(function()
    {
      change_guest()
    });
    $( "#up-usr-button" ).click(function()
    {
      change_user()
    });
});