/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript handles the row for a historical snapshot
 *                  of a given pathway
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Template
    'text!templates/pathway/pathwayHistoryRow.html',

    'globalmodels/contextModel',
    'pathway/modalViews/publishModal',

], function ($, _, Backbone, historyRowTemplate, contextModel,PublishPath) {

    var HistoryRow = Backbone.View.extend({
        tagName: "li class='dd-item history-row'",
        template: _.template(historyRowTemplate),
        events: {
            'click .history-checkbox': 'handleCheck',
            'click .history-select-button': 'handleSelect',
            'click .delete-hist': 'handleDelete'
        },
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            this.model.url = "/history/" + this.model.get("canonical") + "/" + this.model.get('pathid');

            return this;
        },
        handleCheck: function(event){
            if ($(event.target).hasClass("check-disabled")) return;
            new PublishPath({el: '#modal-target', type:'history', elToPublish: this.el , modelToPublish:this.model});

        },
        handleSelect: function() {
            if (contextModel.get('code') == 'undefined') {
                if (contextModel.get('canonical') != this.model.get('canonical')){
                    contextModel.set('code', 'undefined', {silent: true});
                }
            }
            contextModel.set('pathid', String(this.model.get('pathid')))
            contextModel.set('canonical', String(this.model.get('canonical')))

            $(".active-pathway").removeClass("active-pathway");
            $(this.el).addClass("active-pathway")
        },
        handleDelete: function(){

        }
    });

    return HistoryRow;

});
