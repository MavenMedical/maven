$(function() {
	$("#searchb").autocomplete({
		source: "/ac/autocomplete",
		    crossDomain:true,
		    minLength: 2,
		    select: function(event, ui) {
		    var url = ui.item.id;
		    alert('url');
		    if(url != '#') {
			alert(url);
		    }
		},
 
		    html: true, // optional (jquery.ui.autocomplete.html.js required)
 
		    // optional (if other layers overlap autocomplete list)
		    open: function(event, ui) {
		    $(".ui-autocomplete").css("z-index", 1000);
		}
	    });
 
    });

