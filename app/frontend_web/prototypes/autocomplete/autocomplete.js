$(function() {
	$("#searchb").autocomplete({
		source: "/ac/autocomplete",
		    crossDomain:true,
		    minLength: 2,
		    select: function(event, ui) {
		    var url = ui.item.id;


		},

		    html: true, // optional (jquery.ui.autocomplete.html.js required)

		    // optional (if other layers overlap autocomplete list)
		    open: function(event, ui) {
		    $(".ui-autocomplete").css("z-index", 1000);



		}
	    });







  $('#search').autocomplete({
    // source: function() { return "GetState.php?country=" + $('#Country').val();},
      source: function(request, response) {
        $.ajax({
          url: "/ac/autocomplete",
               dataType: "json",
          data: {
            term : request.term,
            patient : $('#searchb').val()
          },
          success: function(data) {
            response(data);
          }

        });
      },
    minLength: 2
  });

 });