$("form input[type=submit]").click(function() {
	//This function sets clicked=true to the input button clicked of the form
    $("input[type=submit]", $(this).parents("form")).removeAttr("clicked");
    $(this).attr("clicked", "true");
});

function objetify_form(array) {
	//This function takes an array = $.serializeArray()
	//and returns a JSON
	var obj = {}
	for (var i=0; i < array.length; i++) {
		obj[array[i].name] = array[i].value;
	}
	return obj;
};

function draw_qrcode(){
	$('.qrcode').each(function() {
		var root = location.origin;
		var client = $(this).attr('client');
		var seat = $(this).attr('seat');
		var text = root + '/client/' + client + '/seat/' + seat;
		$(this).qrcode(text);
	});
};

function tabsfunc() {
	//This function sets the tabs with jQuery UI
    $( "#tabs" ).tabs().addClass( "ui-tabs-vertical ui-helper-clearfix" );
    $( "#tabs li" ).removeClass( "ui-corner-top" ).addClass( "ui-corner-left" );
  };
  
function seats_tabs() {
	//This function sets the tabs of the seats by rooms with jQuery UI
	$( "#rooms" ).tabs().addClass( "ui-tabs-vertical ui-helper-clearfix" );
    $( "#rooms li" ).removeClass( "ui-corner-top" ).addClass( "ui-corner-left" );
};

function seats_accordion() {
	$( ".seats_accordion" ).accordion();
};

function customMenu(node) {
	//This is the context menu of the jstree

	// The default set of all items
	var items = {
		"ccp": false,
		"create": false,
		"rename": false,
		"remove": false,
		"Create": {
			"label": "Create",
			"separator_after": true,
			"submenu": {
				"Section": {
					"label": "Section",
					"action": function (obj) {
						this.create(obj, "inside", {"data": "New Section", "state": "open", "attr":{"rel": "section"}}); 
					}
				},
				"Sub": {
					"label": "Sub-Section",
					"action": function (obj) {
						this.create(obj, "inside", {"data": "New Sub-Section", "state": "open", "attr":{"rel": "subsection"}}); 
					}
				}
			}
		},
		"Insert": {
			"label": "Insert Item",
			"separator_after": true,
			"action": function(obj) {$('#insert_item_modal_button').click()}
		},
		"Edit" : {
			"label": "Edit",
			"submenu": {
				"Cut": {
					"label" : "Cut",
					"action" : function(obj) { this.cut(obj); }
				},
				"Copy" : {
					"label" : "Copy",
					"action": function(obj) { this.copy(obj); }
				},
				"Paste": {
					"label": "Paste",
					"action": function(obj) { this.paste(obj); }
				},
				"Rename" : {
					"label" : "Rename",
					"action" : function (obj) { this.rename(obj); }
				},
				"Remove": {
					"label": "Remove",
					"action": function(obj) { this.remove(obj); }
				}
			}
		},
		"Edit_Item": {
			"label": "Edit Item",
			"action": function(obj) { 
				//Fills the form with the selected item data
				$('#edit_item_form').find('#id_id').val($('.jstree-clicked').parent().attr('id'));
				$('#edit_item_form').find('#id_name').val($('.jstree-clicked').parent().attr('name'));
				$('#edit_item_form').find('#id_price').val($('.jstree-clicked').parent().attr('price'));
				$('#edit_item_form').find('#id_description').val($('.jstree-clicked').parent().attr('description'));
				$('#edit_item_modal_button').click();
			}
		}
	};
	// Cases for each type of node
	switch ($(node).attr('rel')) {
		case 'root':
			delete items.Insert;
			delete items.Edit.submenu.Cut;
			delete items.Edit.submenu.Copy;
			delete items.Edit.submenu.Remove;
			delete items.Edit_Item;
		break;
		
		case 'section':
			delete items.Insert;
			delete items.Edit_Item;
		break;
		
		case 'subsection':
			delete items.Create
			delete items.Edit_Item;
		break;
		
		case 'item':
			delete items.Create
			delete items.Insert;
			delete items.Edit.submenu.Paste;
			delete items.Edit.submenu.Rename;
		break;
	};
	
	return items;
}
  
function treemaker(){  
  	for (var i=0; i<menus.length; i++){
		var j = i + 1;
		$("#tabs-"+ j +"").jstree({
		"json_data": menus[i],
		"types": {
			"valid_children" : ["root"],
			"types": {
				"root" : {
					"valid_children": ["section", "subsection"],
					"icon": {
						"image": "http://static.jstree.com/v.1.0rc/_docs/_drive.png"
					},
					"start_drag" : false,
                    "move_node" : false,
                    "delete_node" : false,
                    "remove" : false
				},
				"section": {
					"valid_children" : ["section", "subsection"]
				},
				"subsection": {
					"valid_children": ["item"]
				},
				"item": {
					"valid_children": "none",
					"icon": {
						"image": "http://static.jstree.com/v.1.0rc/_demo/file.png"
					},
					"rename" : false
				}
			}
		},
		"themes": {
			"theme": "apple"
		},
		"plugins" : [ "themes", "json_data", "ui", "dnd", "crrm", "contextmenu", "hotkeys", "unique", "types" ],
		"contextmenu": {"items": customMenu	},
		});
	};
};  
  
 function tabledisplay() {
	//This function add the the tablesorter and tableFilter to the table of items
	//In the item edit view
	$('#myTable').tablesorter({
		sortList: [[1,0], [2,0]],
		headers: {
			0: { sorter: false },
			4: { sorter: false }
		}
	}).tableFilter();
 };
 
 function item_insert_table() {
	//This function add the the tablesorter and tableFilter to the table of items
	//In the menu edit view
	$('#insert_item_table').tablesorter({
		sortList: [[0,0]]
	}).tableFilter();
	$('#selectable').selectable({
		filter: "td"
	});
 };
 
 function new_menu(){
	//This function adds the new menu in the tabs
	//In the menu edit view
	var name = $('#tabs').children('ul').children('li:last-child').children('a').text();
	var id = $('#tabs').children('ul').children('li:last-child').children('p').text();
	menus.push(eval('({"data": [{"state": "open", "data": "' + name + '", "attr": {"id": "' + id + '", "rel": "root"}, "children": []}]})'));
};

function photo_upload_form_itemname() {
	$('.item_photo').children('a').click(function() {
		var path = $('#upload_photo_form').children('input[name=key]').val().split('/');
		var root = path[0] + '/';
		var client = path[1] + '/';
		var name = $(this).attr('item_id');
		var filename = root + client + name;
		$('#upload_photo_form').children('input[name=key]').val(filename);
	});
};

function validate_password() {
	var pass_1 = $('#new_pass_1').val();
	var pass_2 = $('#new_pass_2').val();

	if (pass_1 != pass_2) {
		$("#validate-status").text('Passwords dont match');
	} else {
		$("#validate-status").text('');
	};
};

function validate_screen_password() {
	var pass_1 = $('#screen_new_pass_1').val();
	var pass_2 = $('#screen_new_pass_2').val();

	if (pass_1 != pass_2) {
		$("#validate-screen-status").text('Passwords dont match');
	} else {
		$("#validate-screen-status").text('');
	};
};

$(document).ready(function() {

	$('#new_pass_1').keyup(validate_password);
	$('#new_pass_2').keyup(validate_password);
	$('#screen_new_pass_1').keyup(validate_screen_password);
	$('#screen_new_pass_2').keyup(validate_screen_password);
	
	draw_qrcode();
	seats_accordion();
    tabledisplay();
	seats_tabs();
	
	$('.delete_button').submit(function() {
		$.ajax({
			data: $(this).serialize(),
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				$(this).find('.ajaxwrapper').html(response);
			}
		});
		$(this).closest('.menu_items').hide();
		return false;	
	});
	
	$('.save_edit_button').submit(function() {
		var name = $(this).parent().siblings('.item_name').text();
		var price = $(this).parent().siblings('.item_price').text();
		var description = $(this).parent().siblings('.item_description').text();
		var form = objetify_form($(this).serializeArray());
		$.ajax({
			data: {
				'csrfmiddlewaretoken': form.csrfmiddlewaretoken,
				'item_id': form.item_id,
				'name': name,
				'price': price,
				'description': description,
				'edit_item': ''
			},
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				$('#myTable').tablesorter();
				$('#myTable').tablesorter();
			}
		});
		return false;
	});
	
	$('#edit_item_form').submit(function() {
		var form = objetify_form($(this).serializeArray());
		$.ajax({
			data: $(this).serialize() + "&edit_item" + "&item_form",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				$('li[id="' + form.item_id + '"]').attr('name', form.name).attr('price', form.price).attr('description', form.description);
				$('li[id="' + form.item_id + '"]').children('a').html('<ins class="jstree-icon">&nbsp;</ins>' + form.name)
				$('#insert_item_loader').load(' #insert_item_table_container', function(){item_insert_table()});
				$('#edit_item_modal').modal('toggle');
			}
		});	
		return false;
	});
	
	$('#create_item_form').submit(function() {
		var button_pressed = $("input[type=submit][clicked=true]").val();
		$.ajax({
			data: $(this).serialize() + "&create_item" + "&item_form",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				$('#table_div').load(' #myTable', function(){
					tabledisplay();
					photo_upload_form_itemname();
				});
				$('#insert_item_loader').load(' #insert_item_table_container', function(){item_insert_table()});
				if (button_pressed == "Create") {
					$('#create_item_modal').modal('toggle');
				}
			}
		});	
		return false;
	});
	
	photo_upload_form_itemname();
	
	$('#file_photo').change(function() {
		var fileField = $('#file_photo').val();
		if (fileField.indexOf('\\') > -1) {
			fileField = fileField.substring(fileField.lastIndexOf('\\') + 1, fileField.length);
		}
		if (fileField.indexOf('/') > -1) {
			fileField = fileField.substring(fileField.lastIndexOf('/') + 1, fileField.length);
		}
		var extension;
		if (fileField.indexOf('.') > -1) {
			extension = fileField.substring(fileField.lastIndexOf('.') + 1, fileField.length);
		} else {
			extension = "";
		}
		var contentType = "application/octet-stream";
		if ( extension == "txt" ) {
			contentType= "text/plain";
		} else if ( extension == "htm" || extension == "html" ) {
			contentType= "text/html";
		} else if ( extension == "jpg" || extension == "jpeg" ) {
			contentType = "image/jpeg";
		} else if ( extension == "gif" ) {
			contentType = "image/gif";
		} else if ( extension == "png" ) {
			contentType = "image/png";
		}
		
		$('#form_content_type').val(contentType);
	});

	$('#upload_photo_form').fileupload({
		maxNumberOfFiles: 1,
		fileInput: $('#file_photo'),
		replaceFileInput: false,
		url: $(this).attr('action'),
		type: $(this).attr('method'),
		autoUpload: false,
		dataType: 'xml',
		add: function (event, data) {
			$('#upload_but').off('click');
			data.context = $("#upload_button").on('click', function (e) {
				data.submit();
			});
		},
		send: function(e, data) {
			$('.progress').fadeIn();
		},
		progress: function(e, data){
			var percent = Math.round((data.loaded / data.total) * 100);
			$('.bar').css('width', percent + '%');
		},
		fail: function(e, data) {
			$('#error_upload_message').fadeIn();
		},
		success: function(data) {
			var form = $('#upload_photo_form');
			form = objetify_form(form.serializeArray());
			var item_id = form.key.split('/')[2];
			$.ajax({
				data: {
					'csrfmiddlewaretoken': form.csrfmiddlewaretoken,
					'item_id': item_id,
					'set_item_photo': ''
				},
				type: 'POST',
				url: "",
				success: function(response) {
					$('#table_div').load(' #myTable', function(){
						tabledisplay();
						photo_upload_form_itemname();
						$('#upload_photo_modal').modal('toggle');
					});
				}
			});
		},
		done: function (event, data) {
			$('.progress').fadeOut(300, function() {
				$('.bar').css('width', 0);
			});
			$('#error_upload_message').fadeOut();
		}
	});

	
	$('#add_menu_form').submit(function() {
		var title = $(this).find('#tab_title').val()
			$.ajax({
				data: $(this).serialize() + "&add_menu",
				type: $(this).attr('method'),
				url: $(this).attr('action'),
				success: function(response) {
					$('#tabs_container').load(' #tabs', function(){tabsfunc(); new_menu(); treemaker(); });					
				}
			});
		return false;
	});
	
	$('#save_menu_form').submit(function() {
		var tree = $('.jstree[aria-expanded="true"]').jstree("get_json", -1);
		var token = $(this).serializeArray()[0];
		$.ajax({
			data: {
				'csrfmiddlewaretoken': token.value,
				'save_menu': '',
				'tree': JSON.stringify(tree)
				},
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				alert("This menu has been saved");
			}
		});
		return false;
	});
	
	$('#active_menu_form').submit(function() {
		var tree = $('.jstree[aria-expanded="true"]').jstree("get_json", -1);
		var token = $(this).serializeArray()[0];
		$.ajax({
			data: {
				'csrfmiddlewaretoken': token.value,
				'active_menu': '',
				'tree': JSON.stringify(tree)
				},
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				alert("This menu has been set as the Active Menu");
			}
		});
		return false;
	});
	
	$('#seats_quantity_form').submit(function(event) {
		event.preventDefault();
		$.ajax({
			data: $(this).serialize() + "&set_seats_quantity",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				$('#seats_div_wrapper').load(' #seats_div', function(){draw_qrcode();});
			}
		});
	});
	
	$('#create_room_form').submit(function(event) {
		event.preventDefault();
		$.ajax({
			data: $(this).serialize() + "&create_room",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				//TODO: new rooms created dont have the ajax functions attach to them
				$('#rooms_container').load(' #rooms', function(){draw_qrcode();	seats_accordion(); seats_tabs(); });	
			}
		});
	});
	
	$('.delete_room_form').submit(function(event) {
		event.preventDefault();
		$.ajax({
			data: $(this).serialize() + "&delete_room",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				$('#rooms_container').load(' #rooms', function(){draw_qrcode();	seats_accordion(); seats_tabs(); });
			}
		});
	});
	
	$('.set_room_menu_form').submit(function(event) {
		event.preventDefault();
		$.ajax({
			data: $(this).serialize() + "&set_room_menu",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				//new menu set
			}
		});
	});
	
	$('.create_seat_form').submit(function(event) {
		event.preventDefault();
		$.ajax({
			data: $(this).serialize() + "&create_seat",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				$('#rooms_container').load(' #rooms', function(){draw_qrcode();	seats_accordion(); seats_tabs(); });
			}
		});
	});
	
	$('.delete_seat_form').submit(function(event) {
		event.preventDefault();
		var form = $(this);
		$.ajax({
			data: $(this).serialize() + "&delete_seat",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				form.parent().hide();
				form.parent().prev().hide();
			}
		});
	});
	
	$('#insert_item_button').click(function() {
		$('.ui-selected').each(function(){
			$('.jstree[aria-expanded="true"]').jstree(
				"create",
				null,
				"inside",
				{
					"data": $(this).children('#item_insert_name').text(),
					"attr": {
						"rel": "item",
						"id": $(this).children('#item_insert_id').text(),
						"name": $(this).children('#item_insert_name').text(),
						"price": $(this).children('#item_insert_price').text(),
						"description": $(this).children('#item_insert_description').text()
					}
				},
				false,
				true
			);
		});
		$('#insert_item_modal').modal('toggle');
	});
	
	$('#change_name_form').submit(function(event) {
		event.preventDefault();
		var form = $(this);
		$.ajax({
			data: $(this).serialize() + "&change_name_form",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				alert('Name changed');
			}
		});
	});
	
	$('#change_password_form').submit(function(event) {
		event.preventDefault();
		var form = $(this);
		var pass_1 = $('#new_pass_1').val();
		var pass_2 = $('#new_pass_2').val();

		if (pass_1 != pass_2) {
			alert('Passwords DONT match!');
		} else {
			$.ajax({
				data: $(this).serialize() + "&change_password_form",
				type: $(this).attr('method'),
				url: $(this).attr('action'),
				success: function(response) {
					alert('Password changed');
				},
				error: function(response) {
					alert('Current password didnt match');
				}
			});
		};
	});
	
	$('#create_screen_user_form').submit(function(event) {
		event.preventDefault();
		var form = $(this);
		$.ajax({
			data: $(this).serialize() + "&create_screen_user_form",
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			success: function(response) {
				$('#users-contain-wrapper').load(' #users-contain');
				$('#create_screen_error').text('');
			},
			error: function(response) {
				$('#create_screen_error').text('Username already registered. Try Another one');
			}
		});
	});
	
	$('.change_screen_user_password_button').click(function (event) {
		var username = $(this).parent().siblings('.screen_username').text();
		$('#change_screen_user_password_username').val(username);
	});
	
	$('#change_screen_user_password_form').submit(function(event) {
		event.preventDefault();
		var form = $(this);
		var pass_1 = $('#screen_new_pass_1').val();
		var pass_2 = $('#screen_new_pass_2').val();

		if (pass_1 != pass_2) {
			alert('Passwords DONT match!');
		} else {
			$.ajax({
				data: $(this).serialize() + "&change_screen_user_password_form",
				type: $(this).attr('method'),
				url: $(this).attr('action'),
				success: function(response) {
					alert('Password changed');
				},
			});
		};
	});
	
	$('.delete_screen_user').click(function (event) {
		var username = $(this).parent().siblings('.screen_username').text();
		$.ajax({
			data: 'username=' + username + '&delete_screen_user',
			url: '',
			success: function(response) {
				$(this).parent().parent().hide();
			}
		});
	});
	
	var parts = location.pathname.split("/");
	var url = parts[parts.length - 1];
    // Will only work if string in href matches with location
        $('ul.nav a[href="./' + url + '"]').parent().addClass('active');
		
	tabsfunc();
	treemaker();
	item_insert_table();
	
	
});
