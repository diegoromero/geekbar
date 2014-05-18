function poll(){
	setTimeout(function(){
		$('.refresh_container').load('screen_refresh/', function() {poll();});
	}, 7830);
};


$(document).ready(function() {
	var parts = location.pathname.split("/");
	var url = parts[parts.length - 2];
	
	if ( url == "orders" ) {
		poll();
	};
});