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
        el: '.page',
        template: _.template(episodeTemplate),
        initialize: function(){
            _.bindAll(this, 'render');
            this.render();
        },
        render: function () {
            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');

            this.$el.html(this.template);

            console.log('test');

            //widgets
            this.patinfo = new PatInfo;
            this.util = new Utilization;
            this.saving = new Saving;
            this.orderable = new Orderable;
            this.dailycost = new DailyCost;
            this.costbd = new CostBD;


        }
    });

    return EpisodeView;

});