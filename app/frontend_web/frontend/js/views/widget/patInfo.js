/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Model
    'models/patientModel',

    'text!templates/widget/patInfo.html'
], function ($, _, Backbone, PatientModel, patInfoTemplate) {

    var PatInfo = Backbone.View.extend({
        el: $('.patientinfo'),
        initialize: function(context){
            _.bindAll(this, 'render');
            this.render(context);
        },
        render: function (context) {

            var pat = new PatientModel;
            console.log(context);

            pat.fetch({
                success: function (pat) {
                    console.log("fetch patient model success");
                    console.log(pat);
                    var template = _.template(patInfoTemplate, {patient:pat});
                    this.$('.patientinfo').html(template);
                },
                data: $.param({ user: 'tom', key: context['key'], patients: context['id']})
            });

        }
    });
    return PatInfo;
});
