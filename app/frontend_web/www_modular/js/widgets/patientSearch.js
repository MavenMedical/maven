/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel', // current patient (if any)
], function ($, _, Backbone,  contextModel) {
    
    var PatSearch = Backbone.View.extend({
	initialize: function(arg){
	    this.template = _.template(arg.template);
	    this.update(contextModel);
	    contextModel.on('change:patients', this.update, this);
	},
	update: function(cm) {
	    if(cm.get('patients')) {
		// for now this is what we do when there is no patient selected
	    } else {
		    this.$el.html(this.template(contextModel.attributes));

            $("#srch-diagnosis").autocomplete({
                source: function(request, response) {
                $.ajax({
                    url: "/autocomplete_diagnosis",
                    term : request.term,
                    data:$.param(contextModel.toParams())+"&diagnosis="+request.term,
                    success: function(data) {
                        response(data);
                    }
                  });
                },
                minLength: 4,
                select: function(event, ui) {
                    if(ui.item){
                        $(event.target).val(ui.item.value);
                        $(event.target.form).submit();
                    }
                }
            });

            var patients = new Array();
            $('#srch-patient').autocomplete({
                source: function(request, response) {
                $.ajax({
                    url: "/autocomplete_patient",
                    term : request.term,
                    patientname : $('#srch-patient').val(),
                    data:$.param(contextModel.toParams())+"&patientname="+request.term,
                    success: function(data) {
                        response(data);
                    }
                  });
                },
                minLength: 2,
                select: function(event, ui) {
                    event.preventDefault(); // prevent the "value" being written back after we've done our own changes

                    if(ui.item){
                        $(event.target).val(ui.item.label);
                       // $(event.target.form).submit();
                        contextModel.set({key:"",
			                patients:ui.item.value,
			                patientName:ui.item.label});
                    }
                }
            });
        }
	}
    });
    return PatSearch;
});