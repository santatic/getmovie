$(document).ready(function() {
	var self = this;

	self.form = $('.form:first');






	// all event
	self.form.on('click', '.generic .add-geter', function(event){
		var link 	= self.form.find('.generic input.link:first').val();
		if (link.length > 0) {
			var body 	= self.form.find('.generic .body');
			var index 	= body.children('tr').length + 1;
			$('<tr class="geter">\
				<td>'+index+'</td>\
				<td>\
					<input type="text" class="form-control input-sm source" value="'+link+'">\
				</td>\
				<td>\
					<div class="progress">\
						<div class="progress-bar" role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">0%</div>\
					</div>\
				</td>\
				<td><button class="btn btn-default btn-generic" type="button">Get</button></td>\
			</tr>').appendTo(body);
		};
	});
	self.form.on('click', '.generic .geter', function(event){
		self.form.find('.generic .geter.active').removeClass('active');
		$(this).addClass('active');

		var data = Base64.decode($(this).attr('data'));
		self.form.find('.movie-json').val(data).trigger('change');
	});
	// generic video
	self.form.on('click', '.generic .body .btn-generic', function(){
		$(this).attr('disabled', 'disabled');
		var geter 		= $(this).parents('.geter:first');
		var link 		= geter.find('input.source').val();
		var process 	= geter.find('.progress .progress-bar');
		var logger 		= self.form.find('.generic .geter-log');
		var ws 			= new WebSocket('ws://'+window.location.host+'/ws');
		//
		ws.onopen 		= function() {
			ws.send(JSON.stringify({
				"url" 		: window.location.href, 
			}));
		};
		ws.onmessage	= function(event) {
			var msg 	= JSON.parse(event.data);
			console.debug(msg);
			if (msg['ok'] == 1) {
				// inited
				ws.onmessage = function(event){
					console.debug('result', event.data)
					var msg 	= JSON.parse(event.data);
					if (msg['ok'] == 1) {
						logger.val(logger.val()+msg['data']['log']+'\n');
						process.css('width', msg['data']['percent']+'%').html(msg['data']['percent']+'%');

						// complete generic
						if (msg['is'] == "finish") {
							ws.close();
							geter.attr('data', Base64.encode(JSON.stringify(msg['data']['data'])));
						};
					}else{
						ws.close();
					};
				};
				logger.val('[+] socket inited\n');
				ws.send(JSON.stringify({
					"action" 	: "generic",
					"link"		: link
				}));
			}else{
				ws.close();
			};
		};
	});









	// modal standar
	self.modal 	= $('<div class="modal fade" role="dialog" aria-hidden="true" data-backdrop="static"><div class="dialog col-md-10 col-md-offset-1"><div class="modal-content"></div></div></div>').modal({ "show": false}).appendTo(self.form);
	self.modal_content = self.modal.find('.modal-content');
	// event change json movie
	self.form.on('change', '.movie-json', function(event){
		self._InfoClear();
		var movie_string 	= $(this).val();
		$(this).val(js_beautify(movie_string,{
						'indent_size': 1,
						'indent_char': '\t'
					}));

		var movie_json 		= $.parseJSON(movie_string);
		var container 		= self.form.find('.movie-info');

		$.each(movie_json, function(key, value){
			if (key == "chap" || key == "movie") {
				console.debug(value);
				var f_chaps = "";
				$.each(value, function(i , chap){
					var f_chap 	= "";
					$.each(chap['server'], function(i, server){
						var f_server = "";
						$.each(server['part'], function(i, part){
							part = $.extend({
								"name":"unknown",
								"link":"",
								"source": [],
								"cache": {}
							}, part);
							var f_part = $('<div class="part name" part-link="'+part['link']+'" part-source="'+Base64.encode(JSON.stringify(part['source']))+'" part-cache="'+Base64.encode(JSON.stringify(part['cache']))+'">'+part['name']+'</div>');
							if (part['link'] == undefined || part['link'] == "") {
								f_part.attr("part-link", "").addClass('alert');
							};
							if (!part['cache']['expire'] && part['link'].split('picasaweb.google.com',2).length > 1) {
								f_part.addClass('nocache');
							};
							f_server += f_part[0].outerHTML;
						});
						f_chap += '<div class="server">'+
										'<div class="name">'+server['name']+'</div>'+
										'<div class="parts">'+f_server+'</div>'+
									'</div>';
					});
					f_chaps += '<div class="chap">'+
								'<div class="name">'+chap['name']+'</div>'+
								'<div class="servers">'+f_chap+'</div>'+
							'</div>';
				});
				self.form.find('.movie-chaps').html(f_chaps);
			}else{
				if($.type(value) == "array") {
					value = value.join('\n');
				}else if ($.type(value) == "object") {
					value = JSON.stringify(value);
				};
				var obj = container.find('[name=' + key +']').val('');
				if (obj.is('textarea')) {
					value = $('<textarea></textarea>').html(value).val();
				};
				obj.val(value);
			};
		});
		// update viewer
		self._InfoView();
	});
	
	// event change info -> generic to update json
	self.form.on('change', '.movie-info [name]', function(event){
		var json = self._InfotoJson();
		self.form.find('.movie-json').val(js_beautify(JSON.stringify(json),{
						'indent_size': 1,
						'indent_char': '\t'
					}));

		// update viewer
		self._InfoView();
	});
	////// change movie chaps/servers/parts info
	self.form.on('click', '.movie-chaps .name', function(){
		self.__current_name_object = $(this);
		if (self.__current_name_object.is('.part')) {
			var form = $('<div class="modal-header"><button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><h4 class="modal-title">Update</h4></div><div class="modal-body"><div class="row"><div class="col-sm-12"><label>Name</label><input type="text" name="name" class="form-control"><label>Link</label><div class="input-group"><input type="text" class="form-control" name="link"><span class="input-group-btn"><button type="button" class="btn btn-default get-cache"><span class="glyphicon glyphicon-cloud-download"></span> Update Cache</button></span></div><label>Cache</label><textarea class="form-control input-sm" name="cache" rows="10"></textarea><label>Source</label><textarea class="form-control" name="source" rows="5"></textarea></div></div></div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal">Close</button><button type="button" class="btn btn-primary movie-update">Update</button></div>');
			var name = self.__current_name_object.html();
			var link = self.__current_name_object.attr('part-link');
			var source = $.parseJSON(Base64.decode(self.__current_name_object.attr('part-source'))).join('\n');
			var cache = js_beautify(Base64.decode(self.__current_name_object.attr('part-cache')));

			form.find('input[name=name]').val(name);
			form.find('input[name=link]').val(link);
			form.find('textarea[name=source]').val(source);
			form.find('textarea[name=cache]').val(cache);
		}else{
			var form = $('<div class="modal-header"><button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><h4 class="modal-title">Update</h4></div><div class="modal-body"><div class="row"><div class="col-sm-12"><label>Movie Name</label><input type="text" name="name" class="form-control"></div></div></div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal">Close</button><button type="button" class="btn btn-primary movie-update">Update</button></div>');
			var name = self.__current_name_object.html();
			form.find('input[name=name]').val(name);
		};
		self.modal_content.html(form);
		self.modal.modal('show');
	});

	// modal update cache
	this.modal.on('click', '.btn.get-cache', function(event){
		var link = self.modal.find('input[name=link]').val();
		$.getJSON(link, function(result){
			var cache = {"video": [], "expire": 0};
			$.each(result['feed']['media']['content'], function(i, v){
				if (v['type'].indexOf("video") == 0) {
					cache['video'].push(v);
					if (!cache['expire']) {
						cache['expire'] = parseInt(v['url'].split('expire=')[1].split('&'));
					};
				};
			});
			self.modal.find('textarea[name=cache]').val(js_beautify(JSON.stringify(cache)));
		});
	});

	// run update
	self.modal.on('click', '.modal-footer .movie-update', function(){
		if (self.__current_name_object != undefined) {
			if (self.__current_name_object.is('.part')) {
				var name 	= self.modal_content.find('input[name=name]').val().trim();
				var link  	= self.modal_content.find('input[name=link]').val().trim();
				var source  = self.modal_content.find('textarea[name=source]').val().trim();
				var cache  = self.modal_content.find('textarea[name=cache]').val().trim();

				var tmp 	= source.split('\n');
				source 		= [];
				$.each(tmp, function(i, v){
					v = v.trim();
					if (v.length > 0) {
						source.push(v);
					};
				});
				console.debug(source);
				try{
					cache = $.parseJSON(cache);
				}catch(e){
					cache = {};
				}
				if (!cache['expire'] && link.split('picasaweb.google.com',2).length > 1) {
					self.__current_name_object.addClass('nocache');
				}else{
					self.__current_name_object.removeClass('nocache');
				};
				self.__current_name_object.html(name);
				self.__current_name_object.attr('part-link', link);
				self.__current_name_object.attr('part-source', Base64.encode(JSON.stringify(source)));
				self.__current_name_object.attr('part-cache', Base64.encode(JSON.stringify(cache)));
			}else{
				var name 	= self.modal_content.find('input[name=name]').val().trim();
				self.__current_name_object.html(name);
			};
			self.modal.modal('hide');
		};
	});

	//////// event import movie
	var modal_import_form = $('<div class="modal-header"><button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><h4 class="modal-title">Import Movie</h4></div><div class="modal-body"><div class="row"><div class="col-sm-12"><label>Current Movie JSON</label><textarea class="form-control" name="movie-json" rows="25"></textarea></div></div></div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal">Close</button><button type="button" class="btn btn-primary movie-import">Import</button></div>');
	// show modal ask for import
	self.form.on('click', '.import', function(event){
		var json = self._InfotoJson();
		var json_string = js_beautify(JSON.stringify(json),{
						'indent_size': 1,
						'indent_char': '\t'
					});
		modal_import_form.find('[name=movie-json]').val(json_string);
		self.modal_content.html(modal_import_form);
		self.modal.modal('show');
	});
	// import action
	self.modal.on('click', '.modal-footer .movie-import', function(){
		var json_string 	= self.modal_content.find('[name=movie-json]').val();
		json_string 		= JSON.stringify($.parseJSON(json_string));
		self.Load({
			"query": {
				"action": "import",
				"movie": json_string
			},
			"callback": function(result){
				if (result['error'] == 0) {
					self.modal.modal('hide');
				};
			}
		});
	});
	this._InfoView = function(){
		var obj_info 	= this.form.find('.movie-info');
		var obj_viewer 	= this.form.find('.movie-viewer');
		
		var poster 		= obj_info.find('[name=poster]').val().trim();
		obj_viewer.find('.poster').attr('src', poster);

		var description 	= obj_info.find('[name=description]').val().trim();
		obj_viewer.find('.description').html(description);

	};
	this._InfotoJson = function(){
		var movie_json 	= {
			"chap": []
		};
		// movies information
		var obj_info 		= this.form.find('.movie-info [name]');
		$.each(obj_info, function(i, v){
			v = $(v);
			var key = v.attr('name');
			var val = v.val();
			if (key == "length") {
				val = $.parseJSON(val);
			};
			if (key != "description" && v.is('textarea')) {
				tmp = val.split('\n');
				val = [];
				$.each(tmp, function(i, v){
					v = v.trim();
					if (v.length > 0) {
						val.push(v);
					};
				});
			};
			movie_json[key] = val;
		});

		// movie chaps
		var obj_chaps 		= this.form.find('.movie-chaps');
		$.each(obj_chaps.find('.chap'), function(i, obj_chap){
			obj_chap = $(obj_chap);
			var chap = {
				"name": obj_chap.children('.name').html().trim(),
				"server": []
			};
			$.each(obj_chap.find('.servers .server'), function(i, obj_server){
				obj_server = $(obj_server);
				var server = {
					"name": obj_server.children('.name').html().trim(),
					"part": []
				};
				$.each(obj_server.find('.parts .part'), function(i, obj_part){
					obj_part = $(obj_part);
					server['part'].push({
						"name": obj_part.html().trim(),
						"link": obj_part.attr('part-link').trim(),
						"source": $.parseJSON(Base64.decode(obj_part.attr('part-source'))),
						"cache": $.parseJSON(Base64.decode(obj_part.attr('part-cache')))
					});
				});
				chap['server'].push(server);
			});
			movie_json['chap'].push(chap);
		});
		return movie_json;
	};
	this._InfoClear = function(){
		// clear info
		var obj_info 		= this.form.find('.movie-info [name]');
		$.each(obj_info, function(i, v){
			v = $(v);
			if (v.is('textarea')) {
				v.html('');
			};
			v.val('');
		});

		// clear chaps
		this.form.find('.movie-chaps').html('');
	};
});