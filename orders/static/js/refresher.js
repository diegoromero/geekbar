var refresh_rate = 7830;

function poll(){
	setTimeout(function(){
		$('.refresh_container').load('screen_refresh/', function() {poll();});
	}, refresh_rate);
};

$(document).ready(function() {
	poll();
});