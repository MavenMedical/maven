/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'currentContext',

    //Model
    'models/patientModel',

    'text!templates/templatesA/widget/patInfo.html'
], function ($, _, Backbone, currentContext,  PatientModel, patInfoTemplate) {

    var PatInfo = Backbone.View.extend({
        el: '.patientinfo',
        template: _.template(patInfoTemplate),
	that: this,
        initialize: function(){
            _.bindAll(this, 'render');
            this.pat = new PatientModel;
        },
	update: function (that, pat) {
		that.$el.html(that.template({patient:pat}));
            }
	});
    return PatInfo;
});
