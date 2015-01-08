/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript handles an interaction row, normally shown when 
 *              hovering over a user
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeContext',
    //Template
    'text!templates/interactionRow.html'
], function ($, _, Backbone, contextModel, treeContext, interactionRowTemplate) {

    var InteractionRow = Backbone.View.extend({
        tagName: "tr class='interaction-row'",
        template: _.template(interactionRowTemplate),
        initialize: function() {
            var that=this
            //$(document).on("swiperight", that.flip())
            contextModel.on('change:nextflips change:page',
                            function() {
                                if (contextModel.get('nextflips') && contextModel.get('page') == 'pathway') {
                                    this.$el.hide()
                                } else {
                                    this.$el.show()
                                }
                            }, this)
        },
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            return this;
        },
        events: {
            'click': 'handleClick'
        },
        handleClick: function() {
            var that=this
            $.ajax({
                url: '/interaction_details', 
                data: that.model.toJSON(), 
                success: function(data) {
                    treeContext.suppressClick=true
                    contextModel.set({historysummary: data.summary, history: data.base, historydetails: that.model, historyposition: 0})
                },
                error: function(a,b) {console.log('error',arguments)},
                dataType: 'json',
                method: 'GET'
            })
        }
    });

    return InteractionRow;

});
