/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
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
    'text!templates/pathway/pathwayFolderEntry.html',
    'pathway/modalViews/newPathway',
    'pathway/modalViews/newPathwayFolder',
     'pathway/models/pathwayCollection',


], function ($, _, Backbone, router, contextModel, pathFolderRowTemplate, NewPathway, NewPathwayFolder, curCollection) {
        console.log(NewPathwayFolder);

    var ruleRow = Backbone.View.extend({
        tagName: "div class='pathway-sub-folder ui-state-default sortable-folder'",
        template: _.template(pathFolderRowTemplate),
        parentList: [], //parent folders
        events: {
            "click .pathway-folder-title": 'toggleFolder',
            "click .add-sub-pathway": 'handleNewPathway',
            "click .add-sub-folder": 'handleNewSubFolder',
        },
        toggleFolder: function(event){
            event.stopPropagation();
            curFolder = $(this.el).find(".pathway-folder-title").first();

            if ($(".folder-state", curFolder).hasClass("glyphicon-folder-close")){
                //open folder - change folder icon to 'open' and show all immediate children
                    $(".folder-state", curFolder).switchClass("glyphicon-folder-close", "glyphicon-folder-open");
                    //$(".ui-state-default", this.$el).css("display","inline-block");
                    curFolder.siblings().css("display","inline-block");
                }
                else {
                    //close folder - change folder icon to 'close' and hide all children
                    $(".folder-state", this.$el).switchClass("glyphicon-folder-open", "glyphicon-folder-close");
                    $(".ui-state-default", this.$el).hide();

                    //curFolder.siblings().hide();
                }
        },
        handleNewPathway: function(event) {
            event.stopPropagation();
            new NewPathway({el: '#modal-target', parentList: this.parentList});
        },
        handleNewSubFolder: function(event) {
            event.stopPropagation();
            var a = new NewPathwayFolder({el: '#modal-target', parentFolder: $(this.el), parentList: this.parentList});
        },
        render: function(){
            that = this;
            $(this.el).html(this.template(this.model.toJSON()));

            /*$(".pathway-folder-title", this.$el).click(function(event){
                event.stopPropagation();
                event.stopImmediatePropagation();
                if ($(".folder-state", that.$el).hasClass("glyphicon-folder-close")){
                    $(".folder-state", that.$el).switchClass("glyphicon-folder-close", "glyphicon-folder-open");
                    $(".ui-state-default", that.$el).css("display","inline-block");
                }
                else {
                    $(".folder-state", that.$el).switchClass("glyphicon-folder-open", "glyphicon-folder-close");
                    $(".ui-state-default", that.$el).hide();
                }
            })*/

               /*            $(this.el).sortable({
                    connectWith: ".sortable-folder",
                });*/


            $(this.el).sortable({
                connectWith: ".sortable-folder",
                items: '> div:not(.pathway-folder-title):not(.ui-folder-placeholder)', //don't allow user to move the folder title
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
                receive: function(event, ui) {
                    //if moving to a new folder, make sure the new folder is open and that items are visible
                    //folder = $(event.target).closest(".pathway-sub-folder");
                    //if (folder){
                        if ($(".folder-state", that.$el).hasClass("glyphicon-folder-close")) {
                            $(".folder-state", that.$el).switchClass("glyphicon-folder-close", "glyphicon-folder-open");
                        }
                        $(".ui-state-default", that.$el).css("display","inline-block");
                    event.stopImmediatePropagation();
                    event.stopPropagation();
                    curCollection.saveOrder();
                    }
                    /*else {
                        $(event.target).closest("display", "inline-block");
                    }*/

            });
            return this;
        },
        initialize: function(params){
            this.model = params.model
            this.parentList = params.parentList;
            this.parentList.push(this.model.attributes.name);
            //$.extend(this.parents, this.parents,[]);
        },
    });

    return ruleRow;

});
