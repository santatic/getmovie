(function($) {
	$.fn.drags = function(opt) {

		opt = $.extend({handle:"",cursor:"move"}, opt);

		if(opt.handle === "") {
			var $el = this;
		} else {
			var $el = this.find(opt.handle);
		}

		return $el.css('cursor', opt.cursor).on("mousedown touchstart", function(e) {
			if(opt.handle === "") {
				var $drag = $(this).addClass('draggable');
			} else {
				var $drag = $(this).addClass('active-handle').parent().addClass('draggable');
			}
			var z_idx = $drag.css('z-index'),
				drg_h = $drag.outerHeight(),
				drg_w = $drag.outerWidth(),
				pos_y = $drag.offset().top + drg_h - e.pageY,
				pos_x = $drag.offset().left + drg_w - e.pageX;
			if (!$drag.data('draggable-move')) {
				$drag.css('z-index', 1000).parent().on("mousemove touchmove", function(e) {
					var drag = $('.draggable').offset({
						top:e.pageY + pos_y - drg_h,
						left:e.pageX + pos_x - drg_w
					});
					if (!drag.data('draggable-up')) {
						drag.on("mouseup touchend", function(e) {
							$(this).removeClass('draggable').css('z-index', z_idx);
						});
						drag.data('draggable-up', true);
						e.preventDefault(); // disable selection
					};
					e.preventDefault(); // disable selection
				});
				$drag.data('draggable-move', true);
				e.preventDefault(); // disable selection
			};
		}).on("mouseup touchend", function() {
			if(opt.handle === "") {
				$(this).removeClass('draggable');
			} else {
				$(this).removeClass('active-handle').parent().removeClass('draggable');
			}
		});
	}
})(jQuery);