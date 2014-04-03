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

    'text!templates/widget/patInfo.html'
], function ($, _, Backbone, currentContext,  PatientModel, patInfoTemplate) {

    var PatInfo = Backbone.View.extend({
        el: '.patientinfo',
        template: _.template(patInfoTemplate),
        initialize: function(){
            _.bindAll(this, 'render');
            this.pat = new PatientModel;
            this.render();
        },
        render: function () {
            var that = this;
            this.pat.fetch({
                success: function (pat) {
                    that.$el.html(that.template({patient:pat}));
                },
                data: $.param(currentContext.toJSON())
            });
             return this;

        }
    });
    return PatInfo;
});
