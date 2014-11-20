
/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Tom DuBois'
 * DESCRIPTION: This Javascript file handle a hierarchy of rulelist view
 *              so we can handle events easier.
 * 
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'router',
    'globalmodels/contextModel',
    'pathway/models/pathwayCollection',
    'text!templates/pathway/pathwayListEntry.html',
    '../../widgets/pathway/historyList',

], function ($, _, Backbone, router, contextModel, pathwayCollection, pathRowTemplate, HistoryList) {

    var ruleRow = Backbone.View.extend({
        tagName: "div class='ui-state-default path-row'",
        template: _.template(pathRowTemplate),
        historyList: null,
        events:{
	      'click .select-button': 'handleSelect',
	      'click .history-button': 'handleHistory',
	      'click .delete-button': 'handleRemove'
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            this.model.url = "/list/" + this.model.get("id");
            /*
            that = this;
            $(document).ready(function(){
                that.$el.closest('.path-header').attr("value", "hello");
             });*/2

            //$(".sortable-folder").sortable("refresh");
           /* if (typeof params !=="undefined"){
                if (typeof params.newly_added != "undefined") {
                    //if ($(this.el).sibling(".pathway-folder-title").child(".folder-state").hasClass("glyphicon-folder-close")) {
                       // $(this.el).siblings(".pathway-folder-title").find(".folder-state").switchClass("glyphicon-folder-close", "glyphicon-folder-open");
                   // }
                    //$(this.el).siblings().css("display", "inline-block");

                    $(this.el).css("display", "inline-block");
                    that = this;
                }
            }*/
            $(this.el).sortable({
                connectWith: ".sortable-folder",
                items: '> div:not(.pathway-folder-title, ui-folder-placeholder, .path-header)', //don't allow user to move the folder title
                helper : 'clone',
                containment: "#avail-paths-list",
                sort: function (event, ui) {
                    //make the sort function more responsive and user friendly
                    //var that = $(this),
                    var el = $(this);//ui.placeholder.parent();
                    var w = ui.helper.outerHeight();
                    el.children().each(function () {
                        if ($(this).hasClass('ui-sortable-helper') || $(this).hasClass('ui-sortable-placeholder'))
                            return true;
                        // If overlap is more than half of the dragged item
                        var dist = Math.abs(ui.position.top - $(this).position().top),
                            before = ui.position.top > $(this).position().top;
                        if ((w - dist) > (w / 2) && (dist < w)) {
                            if (before)
                                $('.ui-sortable-placeholder', el).insertBefore($(this));
                            else
                                $('.ui-sortable-placeholder', el).insertAfter($(this));
                            return false;
                        }
                    });
                },
            });
            return this;
        },
        initialize: function(params){
            this.model = params.model
        },
        handleSelect: function() {
            contextModel.set('pathid', String(this.model.get('id')))
        },
        handleHistory: function() {
            var pathwayHistory = $(".pathway-history-section", this.$el)
            pathwayHistory.toggle();
            if (pathwayHistory.is(":visible")){
                //hide all other history views
                $(".pathway-history-section").not(pathwayHistory).hide();
                if (pathwayHistory.is(":empty")) {
                    //only fetch history if not yet fetched
                    var extraData = {canonical: this.model.get('id')};
                    this.historyList = new HistoryList({el: $(".pathway-history-section", this.$el), extraData: extraData});
                }
            }
        },
    	handleRemove: function() {
            this.model.destroy({success: function(){
                pathwayCollection.fetch()
            }})

            this.undelegateEvents(); // Unbind all local event bindings

            $(this.el).remove(); // Remove view from DOM

            delete this.$el; // Delete the jQuery wrapped object variable
            delete this.el; // Delete the variable reference to this node
    	}
    });

    return ruleRow;

});
