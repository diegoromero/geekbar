var refresh_rate = 7830;

function poll(){
	$('.ui-page-active .refresh_wrapper').load('screen_refresh/ .refresh_container', function(response, status, xml) {
		$('.refresh_container').trigger( "create" );
	});
};

setInterval(poll, refresh_rate);