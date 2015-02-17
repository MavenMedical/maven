/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'globalmodels/patientCollection',
    'singleRow/patientRow',
    'text!templates/patientList.html'
], function ($, _, Backbone, contextModel, patientCollection, PatientRow, patientListTemplate) {
        var PatientList = Backbone.View.extend({
	    template: function() {return '';},
        initialize: function(){
            patientCollection.bind('add', this.addPatient, this);
            patientCollection.bind('reset', this.render, this);
            contextModel.on('change', this.addAll, this);
            this.addAll();
            var patientlist = $('.patientlist', this.$el);
            patientlist.scrollTop(0);
            patientlist.scroll(function() {
            if(patientlist.scrollTop() + patientlist.innerHeight() + 100 >= patientlist[0].scrollHeight) {
                patientCollection.more();
            }
            });
        },
        render: function(){
            template= _.template(patientListTemplate)
            this.$el.html(template({display: contextModel.get('display')}));
            return this;
        },
	    addPatient: function(pat){
            var patientrow = new PatientRow({
                model: pat
            });
            $('.patienttable').append(patientrow.render().el);
        },
	    addAll: function() {
		    if(contextModel.get('patients')) {
		        this.$el[0].style.display='none';
		    }
            else {
		        this.$el[0].style.display='';
		        this.render();
		        for(var pat in patientCollection.models) {
			        this.addPatient(patientCollection.models[pat]);
		        }
		    }

            var patientlist = $('.patientlist', this.$el);
            setTimeout(function() {
                var patientHeight = patientlist.innerHeight();
                if (patientHeight > 0 && patientHeight < parseInt(patientlist.css('max-height'))) {
                    patientCollection.more();
                }
            },500);
	    },
    });

    return PatientList;
});
