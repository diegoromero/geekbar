var refresh_rate = 7830;
var orders = false;
var bills = false;

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

function check(){
	var parts = location.pathname.split("/");
	var url = parts[parts.length - 2];
	console.log('check');
	if ( url == "orders" ) {
		$('.nav-orders').addClass('active');
		orders = true;
		bills = false;
		poll_orders();
	} else if ( url == "bills") {
		$('.nav-bills').addClass('active');
		orders = false;
		bills = true;
		poll_bills();
	};
}


$(document).ready(function() {
	check();
	console.log('ready');
});