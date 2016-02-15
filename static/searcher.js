$(document).ready(function() {
	var self = this;

	self.form = $('.form:first');

	self.form.on('click' ,'.btn.search', function(event){
		$(this).attr('disabled', 'disabled');
		var search 		= self.form.find('input.search').val();
		var logger 		= self.form.find('.log');
		var ws 			= new WebSocket('ws://'+window.location.host+'/ws');
		//
		ws.onopen 		= function() {
			ws.send(JSON.stringify({
				"search" 		: search, 
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

						var result = self.form.find('.result');
						for (var i in msg['data']['data']) {
							console.debug(i);
							var ms = msg['data']['data'][i];
							for (var j in ms) {
								var m = ms[j];
								console.debug(m);
								var domain = m['link'].split('/',4)[2];

								var obj = result.find('.domain[of="'+domain+'"]');
								if (obj.length == 0) {
									obj = $('<div class="domain row" of="'+domain+'"><label>'+domain+'</label><div class="movies"></div></div>');
									result.append(obj);
								};
								obj.append('<div class="col-sm-6"><a target="_blank" href="'+m['link']+'"><div class="col-sm-3 img"><img src="'+m['image']+'" style="width:100%"></div><div class="col-sm-9"><div class="title">'+m['title']+'</div></div></a></div>');
							};
						};
						// complete generic
						if (msg['is'] == "finish") {
							ws.close();
							alert('finished !');
						};
					}else{
						ws.close();
					};
				};
				logger.val('[+] socket inited\n');
				ws.send(JSON.stringify({
					"action" 	: "search",
					"search"	: search
				}));
			}else{
				ws.close();
			};
		};
	});
});