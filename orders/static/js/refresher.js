//refresh suspended while dev


var refresh_rate = 7830;
var refresh_active = true;

(function poll(){
	setTimeout(function(){
		$('.ui-page-active .refresh_wrapper').load('screen_refresh/ .refresh_container', function() {
			refresh_active = true;
			$('.refresh_container').trigger( "create" );
			console.log('refreshed');
			poll();
		});
	}, refresh_rate);
})();

$("document").on("pageshow",function(event){
	console.log('pageshow');
});
$(document).on("pagecreate",function(event){
  console.log('pagecreate');
  console.log(refresh_active);
});
$(document).on("pagecontainerload",function(event,data){
  console.log('pagecontainerload');
});