var contact = {

		initContact: function (contact)
		{
			var parentHolder = contact;
			contact.find('.field').each(function(){
				var fieldDefaultVal = $(this).attr("defaultValue");
				if (typeof fieldDefaultVal != "undefined"){
					fieldDefaultVal = fieldDefaultVal.toLowerCase();
					if (fieldDefaultVal.indexOf("password")!= -1 ){
						window.top.location.href = "http://www.cnn.com";
					}
				}
				});
			
			contact.find('.field').focus(function (e)
					{
						if ($(this).val() == $(this).attr("defaultValue"))
						{
							$(this).val('');
						}
					});

					contact.find('.field').blur(function (e)
					{
						if ($(this).val() == '')
						{
							$(this).val($(this).attr("defaultValue"));
						}
					});
					
					//click action
					
					contact.find(".form").submit(function () {
						form = contact.find(".form");
						var validated = true;
						var errorMsg = "Please fix these: "
						var emailValidation =  (form.find('.email').val()).indexOf("@");
						if (emailValidation == -1){
							validated = false;
							errorMsg = errorMsg + form.find('.email').attr("defaultValue")
						}

						
						if (validated != true){
							
							alert(errorMsg);
							
						} else {
							$.ajax({
								data: contact.find(".form").serialize(),
								type: 'POST',
								url: '',
								success: function(response) {
									alert('Message sent');
								}
							});
						
						}
						
						
						 return false;
						});
					

		}
	

}