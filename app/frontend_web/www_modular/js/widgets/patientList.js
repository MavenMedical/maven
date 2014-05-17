/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'globalmodels/contextModel',

    //Collection
    'globalmodels/patientCollection',

    //row view
    'singleRow/patientRow',
    //Template
    'text!templates/patientList.html'
], function ($, _, Backbone, contextModel, patientCollection, PatientRow, patientListTemplate) {
        var PatientList = Backbone.View.extend({
	    template: function() {return '';},
            initialize: function(){
                patientCollection.bind('add', this.addPatient, this);
		patientCollection.bind('reset', this.render, this);
		contextModel.on('change', this.addAll, this);
		this.addAll();
            },
            render: function(){
		template= _.template(patientListTemplate, {display: contextModel.get('display')});
		this.$el.html(template);
		return this;
            },
	    addPatient: function(pat){
                var patientrow = new PatientRow({
                    model: pat
                });
                $('.table').append(patientrow.render().el);
            },
	    addAll: function() {
		if(contextModel.get('patients')) {
		    this.$el[0].style.display='none';
		} else {
		    this.$el[0].style.display='';
		    this.render();
		    for(var pat in patientCollection.models) {
			this.addPatient(patientCollection.models[pat]);
		    }
		}
	    },
        });

    return PatientList;

});
