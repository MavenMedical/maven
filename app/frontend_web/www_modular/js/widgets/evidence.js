/**
 * Created by devel on 3/27/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/evidence.html'
], function ($, _, Backbone, evidenceTemplate) {

    var Evidence = Backbone.View.extend({
        el: '#modal-target',
        template: _.template(evidenceTemplate),
        initialize: function (options) {
	    this.evi = options['evi'];
            _.bindAll(this, 'render');
	    this.render();
        },
        render: function () {
	    evidence_text=this.template({alert: this.evi});
	    //console.log(evidence_text);
	    this.$el.append(evidence_text);
	    return this;
        }
    });
    return Evidence;
});
