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

    'text!templates/widget/orderable.html'
], function ($, _, Backbone, currentContext, PatientModel, PatientCollection, orderableTemplate) {

    var Orderable = Backbone.View.extend({
        el: '.orderable',
        template: _.template(orderableTemplate),

        initialize: function () {
            console.log("ini orderable");
            _.bindAll(this, 'render', 'click');
            this.patients = new PatientCollection();
            this.render();
        },

        events: {
            'click': 'click'
        },

        click: function (e) {
            console.log($(e.target));
        },

        render: function () {
            console.log("render orderables");

             var that = this;

            this.patients.fetch({
               success: function(patients){
                   that.$el.html(that.template({patients:patients.models}));
               } ,
                data: $.param(currentContext)
            });
        }
    });
    return Orderable;
});
