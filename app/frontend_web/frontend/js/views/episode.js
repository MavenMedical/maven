/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'views/widget/patInfo',
    'views/widget/utilization',
    'views/widget/saving',
    'views/widget/orderable',

    'views/chart/dailycost',
    'views/chart/costbd',


    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/episode.html'
], function ($, _, Backbone, PatInfo, Utilization, Saving, Orderable, DailyCost, CostBD, episodeTemplate) {

    var EpisodeView = Backbone.View.extend({
        el: $('.page'),
        render: function () {
            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');

            var template = _.template(episodeTemplate, {});
            this.$el.html(template);

            //widgets
            var patinfo = new PatInfo;
            patinfo.render();

            var util = new Utilization;
            util.render();

            var saving = new Saving;
            saving.render();

            var orderable = new Orderable;
            orderable.render();

            var dailycost = new DailyCost;
            dailycost.render();

            var costbd = new CostBD;
            costbd.render();

        }
    });

    return EpisodeView;

});