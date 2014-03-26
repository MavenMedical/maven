/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'views/widget/alert',

    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/alerts.html'
	], function ($, _, Backbone, AlertList, alertTemplate) {

    var AlertsView = Backbone.View.extend({
        el: $('.page'),
        render: function () {
            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');

            $('.patientinfo').empty();

            var template = _.template(alertTemplate, {});
            this.$el.html(template);

            //widgets
            var alertlistview = new AlertList;
            alertlistview.render();

        }
    });

    return AlertsView;

});