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
    'currentContext',
    //views
    'views/widget/patInfo',
    'views/widget/utilization',
    'views/widget/saving',
    'views/widget/orderable',
    'views/chart/dailycost',
    'views/chart/orderbd',
    'views/widget/alert',

    //Collection
    'collections/orders',

    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/episode.html'
], function ($, _, Backbone,currentContext, PatInfo, Utilization, Saving, Orderable, DailyCost, OrderBD, Alert,OrderCollection, episodeTemplate) {

    var EpisodeView = Backbone.View.extend({
        el: '.page',
        template: _.template(episodeTemplate),
        initialize: function(){
            this.render();
        },
        render: function () {
            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');

            this.$el.html(this.template);

            //widgets
            this.patinfo = new PatInfo;
            this.util = new Utilization;
            this.saving = new Saving;
            this.orderable = new Orderable;
            this.dailycost = new DailyCost;
            this.orderbd = new OrderBD;
            this.alert = new Alert;

            this.orders = new OrderCollection();
            this.orders.on('add' , this.orderable.addOrder);
            this.orders.on('sync', this.orderbd.update); //called when fetch is success
            this.orders.fetch({data:$.param(currentContext.toJSON())});


            return this;
        }
    });

    return EpisodeView;

});