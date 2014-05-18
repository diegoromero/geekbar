var refresh_rate = 7830;

function poll_orders(){
	setTimeout(function(){
		$('.refresh_container').load('screen_refresh/', function() {poll_orders();});
	}, refresh_rate);
};

function poll_bills(){
	setTimeout(function(){
		$('.refresh_container').load('screen_refresh_bills/', function() {poll_bills();});
	}, refresh_rate);
};


$(document).ready(function() {
	var parts = location.pathname.split("/");
	var url = parts[parts.length - 2];
	
	if ( url == "orders" ) {
		poll_orders();
	} else if ( url == "bils") {
		poll_bills();
	};
});