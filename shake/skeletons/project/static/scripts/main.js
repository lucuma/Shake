(function($){ "use strict";

	function setupCSRFToken() {
		/* To use the CSRF protection with AJAX calls.
		This will cause all AJAX requests to send back the CSRF token in 
		the custom X-CSRFTOKEN header. */
		window.CSRFToken = $('meta[name="csfrtoken"]').attr('content');
		
		$.ajaxSetup({
			beforeSend: function(xhr, settings) {
				var isAbsoluteUrl = /^[a-z0-9]+:\/\/.*/.test(settings.url);
				// Only send the token to relative URLs i.e. locally.
				if (! isAbsoluteUrl) {
					xhr.setRequestHeader("X-CSRFToken", window.CSRFToken);
				}
			}
		});
	}

	setupCSRFToken();

}(window.jQuery));
