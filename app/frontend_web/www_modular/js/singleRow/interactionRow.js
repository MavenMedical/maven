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

    var flip=function() {
        var nextcode = contextModel.get('nextcode')
        if (nextcode) {
            var navstring = 'pathway/' + contextModel.get('pathid')
                + '/node/-' + nextcode + '/patient/' + contextModel.get('patients')
                + '/' + contextModel.get('enc_date')
            console.log(navstring)
            Backbone.history.navigate(navstring, true)
        }
    }
    var keyflip =  function(evt) {
        if (evt.keyCode == 13 || evt.keyCode == 39) {
	    evt.preventDefault()
            flip()
        }
    }
    
    $(document).keydown(function(evt) {keyflip(evt)})

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
                    var nodes =_.uniq(_.map(_.pluck(data, 'node_id'), function(x) {return x.trim()}), true).join('_')
                    var date = data[0].datetime.slice(0,10)
                    treeContext.suppressClick=true
                    var navstring = 'pathway/' + that.model.get('protocol') + '/node/-' + nodes
                        + '/patient/' + that.model.get('patient') + '/' + date
                    Backbone.history.navigate(navstring, true)
                },
                error: function(a,b) {console.log('error',arguments)},
                dataType: 'json',
                method: 'GET'
            })
        }
    });

    return InteractionRow;

});
