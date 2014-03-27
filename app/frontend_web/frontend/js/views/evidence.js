/**
 * Created by devel on 3/27/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone


    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/evidence.html'
	], function ($, _, Backbone, evidenceTemplate) {

    var EvidenceView = Backbone.View.extend({
        el: $('.page'),
        render: function () {
            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');
            $('.patientinfo').empty();
            console.log("evidence");
            var template = _.template(evidenceTemplate, {});
            this.$el.html(template);

        }
    });

    return EvidenceView;

});
