/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This is the Episode view were all widgets that are needed to
 *              be in the episode page are rendered here.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/

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
        initialize: function(context){
            _.bindAll(this, 'render');
            this.context = context;
            this.render();
        },
        render: function () {
            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');
            console.log(this.context);
            var template = _.template(episodeTemplate, {});
            this.$el.html(template);

            //widgets
            var patinfo = new PatInfo(this.context);

            var util = new Utilization;
            util.render();

            var saving = new Saving;
            saving.render();

            var orderable = new Orderable;

            var dailycost = new DailyCost;
            dailycost.render();

            var costbd = new CostBD;
            costbd.render();

        }
    });

    return EpisodeView;

});