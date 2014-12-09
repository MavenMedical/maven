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
    'text!templates/interactionRow.html',

], function ($, _, Backbone, contextModel, treeContext, interactionRowTemplate) {

    var InteractionRow = Backbone.View.extend({
        tagName: "tr class='interaction-row'",
        template: _.template(interactionRowTemplate),
        initialize: function() {
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
                    console.log(data)
                    var nodes =_.map(_.pluck(data, 'node_id'), function(x) {return x.trim()})
                    var next = nodes[0]
                    var date = data[0].datetime.slice(0,10)
                    var nextflips= nodes.slice(1)
                    treeContext.suppressClick=true
                    contextModel.set({nextflips: nextflips})
                    Backbone.history.navigate('pathway/' + that.model.get('protocol') + '/node/-' + next 
                                             + '/patient/' + that.model.get('patient') + '/' + date, true)
                    console.log('should have navigated')
                },
                error: function(a,b) {console.log('error',arguments)},
                dataType: 'json',
                method: 'GET'
            })
        }
    });

    return InteractionRow;

});
