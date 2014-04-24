$(document).on('pageshow', function() {
	$('.carousel').owlCarousel();
	$('.rm_h').show();
	$('.plus').on('click', function() {
		var quant = parseInt($(this).siblings('.quantity').text());
		quant++;
		$(this).siblings('.quantity').text(quant.toString());
		$(this).parents('.fs').children('form').children('input[name=quantity]').val(quant);
	});
	$('.minus').on('click', function() {
		var quant = parseInt($(this).siblings('.quantity').text());
		if (quant > 1) {
			quant--;
			$(this).siblings('.quantity').text(quant.toString());
			$(this).parents('.fs').children('form').children('input[name=quantity]').val(quant);
		};
	});
});