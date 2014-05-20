//refresh suspended while dev


var refresh_rate = 7830;

(function poll(){
	setTimeout(function(){
		$('.refresh_container').load('screen_refresh/ .refresh_container', function() {
			$('.refresh_container').trigger( "create" );
			console.log('refreshed');
			poll();
		});
	}, refresh_rate);
})();


