/**
 * Created by devel on 3/27/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
], function ($, _, Backbone) {

    var Evidence = Backbone.View.extend({
        el: '#modal-target',
        initialize: function (options) {
	    this.evi = options['evi'];
            _.bindAll(this, 'render');
	    this.render();
        },
        render: function () {
	    var that = this;
	    require(['text!../evidence/'+that.evi+'.html'],
		    function(evidenceTemplate) {
			var template=_.template(evidenceTemplate);
			var evidence_text=template({alert: that.evi});
			//console.log(evidence_text);
			that.$el.append(evidence_text);
			$('#evidence-'+that.evi).modal();
		    });
	    return that;
        }
    });
    return Evidence;
});
