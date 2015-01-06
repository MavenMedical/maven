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

], function ($, _, Backbone, historyRowTemplate, contextModel) {

    var HistoryRow = Backbone.View.extend({
        tagName: "li class='dd-item history-row'",
        template: _.template(historyRowTemplate),
        events: {
            'click .history-checkbox': 'handleCheck',
            'click .history-select-button': 'handleSelect'
        },
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            this.model.url = "/history/" + this.model.get("canonical") + "/" + this.model.get('pathid');

            return this;
        },
        handleCheck: function(event){
            if ($(event.target).hasClass("check-disabled")) return;

            var r = confirm("Are you sure you want to push this version of the pathway into production?")
            if (r != true) return;

            $(this.el).parent().find(".history-checkbox").switchClass("glyphicon-check", "glyphicon-unchecked")
            $(this.el).parent().find(".history-checkbox").attr('title','Use This Snapshot');
            $(".history-checkbox", this.$el).switchClass("glyphicon-unchecked", "glyphicon-check");
            $(".history-checkbox", this.$el).attr('title','');
            //$(this.el).trigger("change");
            this.model.save();
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
        }
    });

    return HistoryRow;

});
