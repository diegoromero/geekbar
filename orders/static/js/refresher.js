//refresh suspended while dev


var refresh_rate = 7830;

(function poll(){
	setTimeout(function(){
		$('.refresh_container').load('screen_refresh/ ul', function() {poll();});
	}, refresh_rate);
})();


