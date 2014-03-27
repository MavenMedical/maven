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
    'text!templates/widget/patientList.html'
], function ($, _, Backbone, currentContext, patientRow,  PatientModel, PatientCollection, patientListTemplate) {
        var PatientList = Backbone.View.extend({
            el: '.patientlist',
            template: _.template(patientListTemplate),

            initialize: function(){
                console.log("patient list ini");
                _.bindAll(this, 'render', 'addPatient');
                this.patients = new PatientCollection;
                this.patients.bind('add', this.addPatient, this);
                this.patients.fetch({data:$.param(currentContext)});
                this.render();
            },
            render: function(){
                console.log('patient list render');
                this.$el.html(this.template);
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
