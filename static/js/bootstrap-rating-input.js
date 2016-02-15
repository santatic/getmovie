(function ($) {

	$.fn.rating = function (opt) {

		var element;
		opt = $.extend({editable: true, max: 5, min: 0, default: 0, note: [], onChange: function(){}}, opt);
		// A private function to highlight a star corresponding to a given value
		function _paintValue(ratingInput, value, active_icon, inactive_icon) {
			var selectedStar = $(ratingInput).find('[data-value="' + value + '"]');
			selectedStar.removeClass(inactive_icon).addClass(active_icon);
			selectedStar.prevAll('[data-value]').removeClass(inactive_icon).addClass(active_icon);
			selectedStar.nextAll('[data-value]').removeClass(active_icon).addClass(inactive_icon);
			// note
			// if (selectedStar.data('note')) {
			// 	ratingInput.parent().children('.rating-note').html(selectedStar.data('note'));
			// };
		}

		// A private function to remove the highlight for a selected rating
		function _clearValue(ratingInput, active_icon, inactive_icon) {
			try{
				var self = $(ratingInput);
				self.find('[data-value]').removeClass(active_icon).addClass(inactive_icon);
				// ratingInput.parent().children('.rating-note').html('');
			}catch(e){}
		}

		// A private function to change the actual value to the hidden field
		function _updateValue(input, val) {
			input.val(val).trigger('change');
			if (val === input.data('empty-value')) {
				input.siblings('.rating-clear').hide();
			} else {
				input.siblings('.rating-clear').show();
			}
		}

		// Iterate and transform all selected inputs
		for (element = this.length - 1; element >= 0; element--) {

			var el, i,
				originalInput = $(this[element]),
				max = originalInput.data('max') || opt.max,
				min = originalInput.data('min') || opt.min,
				def_val = originalInput.val() || opt.default,
				lib = originalInput.data('icon-lib') || 'glyphicon'
				active = originalInput.data('active-icon') || 'glyphicon-star',
				inactive = originalInput.data('inactive-icon') || 'glyphicon-star-empty',
				clearable = originalInput.data('clearable') || null,
				clearable_i = originalInput.data('clearable-icon') || 'glyphicon-remove',
				stars = '';

			// HTML element construction
			for (i = min; i <= max; i++) {
				// Create <max> empty stars
				if(i <= def_val){
					s = ['<i class="',lib, ' ', active, '" data-value="', i];
				}else{
					s = ['<i class="',lib, ' ', inactive, '" data-value="', i];
				}
				if (opt.note.length > 0 && opt.note[i - min]) {
					s.push('" data-toggle="tooltip" data-placement="top" title="' + opt.note[i - min]);
				};
				s.push('"></i>');
				stars += s.join('');
			}
			// Add a clear link if clearable option is set
			if (clearable) {
					stars += [
					' <a class="rating-clear" style="display:none;" href="javascript:void">',
					'<span class="',lib,' ',clearable_i,'"></span> ',
					clearable,
					'</a>'].join('');
			}

			// Clone with data and events the original input to preserve any additional data and event bindings.
			var newInput = originalInput.clone(true)
				.addClass('hidden')
				.data('max', max)
				.data('min', min)
				.data('icon-lib', lib)
				.data('active-icon', active)
				.data('inactive-icon', inactive);

			// Rating widget is wrapped inside a div
			el = [
				'<div class="rating-input" style="float:left;">',
				stars,
				'</div>'].join('');
			el = $(el);
			// Replace original inputs HTML with the new one
			if (originalInput.parents('.rating-input').length <= 0) {
				originalInput.replaceWith(el.append(newInput));
			}
			// // tooltip
			// $.each(el.find('[data-toggle=tooltip]'), function(i, v){
			// 	$(v).tooltip({placement: 'top', title: 'ass'});
			// });

			// if (opt.note.length > 0) {
			// 	el.after('<div class="rating-note" style="padding-left:5px;float:left;"></div>');
			// };
			if (opt.editable) {
				// Give live to the newly generated widgets
				el
				// Highlight stars on hovering
				.on('mouseenter', '[data-value]', function () {
					var self = $(this);
					input = self.siblings('input');
					_paintValue(self.closest('.rating-input'), self.data('value'), input.data('active-icon'), input.data('inactive-icon'));
				})
				// View current value while mouse is out
				.on('mouseleave', '[data-value]', function () {
					var self = $(this),
						input = self.siblings('input'),
						val = input.val(),
						min = input.data('min'),
						max = input.data('max'),
						active = input.data('active-icon'),
						inactive = input.data('inactive-icon');
					if (val >= min && val <= max) {
						_paintValue(self.closest('.rating-input'), val, active, inactive);
					} else {
						_clearValue(self.closest('.rating-input'), active, inactive);
					}
				})
				// Set the selected value to the hidden field
				.on('click', '[data-value]', function (e) {
					var self = $(this),
						val = self.data('value'),
						input = self.siblings('input');
					_updateValue(input,val);
					opt.onChange(val);
					e.preventDefault();
					return false;
				})
				// Remove value on clear
				.on('click', '.rating-clear', function (e) {
					var self = $(this),
						input = self.siblings('input'),
						active = input.data('active-icon'),
						inactive = input.data('inactive-icon');
					_updateValue(input, input.data('empty-value'));
					_clearValue(self.closest('.rating-input'), active, inactive);
					e.preventDefault();
					return false;
				})
				// Initialize view with default value
				.each(function () {
					var input = $(this).find('input'),
						val = input.val(),
						min = input.data('min'),
						max = input.data('max');
					if (val !== "" && +val >= min && +val <= max) {
						_paintValue(this, val);
						$(this).find('.rating-clear').show();
					}
					else {
						input.val(input.data('empty-value'));
						_clearValue(this);
					}
				});
			};
		}
	};

	// Auto apply conversion of number fields with class 'rating' into rating-fields
	// $(function () {
	//	 if ($('input.rating[type=number]').length > 0) {
	//		 $('input.rating[type=number]').rating();
	//	 }
	// });

}(jQuery));
