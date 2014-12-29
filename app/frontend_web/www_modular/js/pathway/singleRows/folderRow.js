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

], function ($, _, Backbone, router, contextModel, pathFolderRowTemplate, NewPathway, NewPathwayFolder) {
        console.log(NewPathwayFolder);

    var ruleRow = Backbone.View.extend({
        tagName: "li class='sub-folder dd-item dd2-item dd-collapsed'",
        template: _.template(pathFolderRowTemplate),
        parentList: [], //parent folders
        events: {
            //"click .pathway-folder-title": 'toggleFolder',
            "click .glyphicon-folder-open": 'closeFolder',
            "click .glyphicon-folder-close": 'openFolder',
            "click .add-sub-pathway": 'handleNewPathway',
            "click .add-sub-folder": 'handleNewSubFolder',
            "click .delete-folder": 'handleDeleteFolder'
        },
        openFolder: function(event){
            //open folder - change folder icon to 'open' and show all immediate children
            $(event.target).closest(".sub-folder").switchClass("dd-collapsed", "dd-expanded",0);
        },
        closeFolder: function(event){
            //close folder - change folder icon to 'close' and hide all children
            $(event.target).closest(".sub-folder").switchClass("dd-expanded", "dd-collapsed",0);
            $(event.target).closest(".sub-folder").find(".sub-folder").switchClass("dd-expanded", "dd-collapsed",0);
        },
        setParents: function(){
            //check the location of the folder - if it has moved, update the parent list and return true

            var newParentList = [$(this.el).children().first().attr("name")]; //initialize with current folder name [this.parentList[this.parentList.length-1]];
            var parentFolder = $(this.el).parent().closest(".sub-folder");
            while (parentFolder.length){
                parentName = parentFolder.children(".pathway-folder-title").attr('name');
                if (typeof parentName=='undefined' || parentName=="") break;
                newParentList.push(parentName);
                parentFolder = $(parentFolder).parent().closest(".sub-folder");
            }
            newParentList.reverse();
            this.parentList = newParentList;
            return newParentList;
        },
        handleNewPathway: function(event) {
            event.stopPropagation();

            new NewPathway({el: '#modal-target', parentList: this.setParents()});
        },
        handleDeleteFolder: function(event) {
            event.stopPropagation();
            if ($(".path-row", this.$el).length) {
                var r = confirm("WARNING: This will delete all contained pathways. Are you sure you want to do this?");
                if (!r) return;
            }
            this.deleteFolderAndPathways($(this.el), this);
        },
        deleteFolderAndPathways: function(folderSelector, that){
            $(folderSelector).children(".sub-folder-contents").children().each(function() {
                //delete all children
                if ($(this).hasClass("pathrow-item")){
                    //current child is a pathway
                    var canonical = $(this).children(".path-row").attr("id");
                    $.ajax({
                        type: 'DELETE',
                        dataType: 'json',
                        url: "/list/" +canonical,
                        error: function (){
                            alert("Could not delete pathway");
                        }
                    });
                }
                else{
                    //current child is a folder
                    that.deleteFolderAndPathways(this, that);
                }
            });

            this.undelegateEvents(); // Unbind all local event bindings

            $(this.el).remove(); // Remove view from DOM

            delete this.$el; // Delete the jQuery wrapped object variable
            delete this.el; // Delete the variable reference to this node
        },
        handleNewSubFolder: function(event) {
            event.stopPropagation();
            this.setParents();
            var a = new NewPathwayFolder({el: '#modal-target', parentFolder: $(this.el).children('ol').first(), parentList: this.parentList});
        },
        render: function(){
            that = this;
            $(this.el).html(this.template(this.model.toJSON()));

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
