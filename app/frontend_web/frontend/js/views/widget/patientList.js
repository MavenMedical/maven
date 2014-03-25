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

    //Collection
    'collections/patients',

    //Template
    'text!templates/widget/patientList.html'
], function ($, _, Backbone, currentContext,  PatientModel, PatientCollection, patientListTemplate) {


    var PatientList = Backbone.View.extend({
        el: '.patientlist',
        template: _.template(patientListTemplate),
        initialize: function(){
            _.bindAll(this , 'render', 'click');
            this.patients = new PatientCollection();
            this.render();

        },
        events: {
          'click tr': 'click'
        },
        click: function(e){
          //console.log($(e.target));
           // console.log($(e.target).text());
            console.log($(e.target.item));
        },
        render: function(){
            console.log(currentContext);
            var that = this;

            this.patients.fetch({
               success: function(patients){
                   that.$el.html(that.template({patients:patients.models}));
               } ,
                data: $.param(currentContext)
            });

        }
    });
    return PatientList;
});
