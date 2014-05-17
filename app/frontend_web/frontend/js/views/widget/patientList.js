/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'currentContext',

    //sub view
    '../singleRow/patientRow',

    //Model
    'models/patientModel',

    //Collection
    'collections/patients',

    //Template
    'text!templates/templatesA/widget/patientList.html'
], function ($, _, Backbone, currentContext, patientRow,  PatientModel, PatientCollection, patientListTemplate) {
        var PatientList = Backbone.View.extend({
            el: '.patientlist',

            initialize: function(){
                _.bindAll(this, 'render', 'addPatient');
                this.patients = new PatientCollection;
                this.patients.bind('add', this.addPatient, this);
                this.patients.fetch({ data:$.param(currentContext.toJSON())});
                this.render();
            },
            render: function(){
		    var template= _.template(patientListTemplate, {display: currentContext.get('display')});

		    this.$el.html(template);
		    return this;
            },
            addPatient: function(pat){
                var patientrow = new patientRow({
                    model: pat
                });
                $('.table').append(patientrow.render().el);
            }
        });

    return PatientList;

});
