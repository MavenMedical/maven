/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/pathwayCollection',
    'pathway/models/treeModel',
    'pathway/modalViews/newPathway',

    'pathway/singleRows/pathRow',
    'text!templates/pathway/pathwaysList.html',

    'pathway/modalViews/newPathwayFolder',
    'pathway/singleRows/folderRow',


], function ($, _, Backbone,  curCollection, curTree,  NewPathway, PathRow, pathwaysListTemplate, newPathwayFolder, FolderRow) {

    var PathwaysList = Backbone.View.extend({
        template: _.template(pathwaysListTemplate),
        events: {
            'click #newpath-button': 'handle_newPath',
            'click #save-button': 'handle_save',
            'click #paths-list-add-folder': 'handle_new_folder'
        },
	initialize: function(){
	    //curCollection.on('sync', this.render, this)
        curCollection.bind('add', this.addNewPathway, this);

        this.render();
        console.log(newPathwayFolder);
	},
    renderFolder: function(folderName, children, parentFolder, that) {
        var thisModel = new Backbone.Model({name: folderName});
        var thisRow = new FolderRow({model: thisModel})
        parentFolder.append(thisRow.render().$el);
        $.each(children, (function(index, value){
            that.renderFolder(index, value, thisRow.$el, that);
        }));
    },
    addNewPathway: function(model){
        this.insertPathway(model, true);
    },
    insertPathway: function(model, newlyAdded){
        //given a pathway's location, add it to the proper folder; if folder doesn't exist, create it
        /*if (path == ""){
            return "#avail-paths-list";
        }*/
        var currentEl = $("#avail-paths-list");
        var path = model.get('folder');

        if (path!=null && path!="") {
            var folders = path.substring(1).split('/');

            //$.each(folders, function(index,value){
            for (var i = 0; i < folders.length; i++) {
                //var curFolder = $(currentEl).children(".pathway-sub-folder");
                var foundFolder = false;
                $.each(currentEl.children(".pathway-sub-folder"), function () {
                    var title = $(this).children(".pathway-folder-title").attr("name");
                    if (title == folders[i]) {
                        currentEl = $(this);
                        foundFolder = true;
                        return false;
                    }
                });                //.children(".folder-title[name='" + folders[i] + "']");
                if (foundFolder) {
                    //folder exists
                    continue;
                    //currentEl = $(curFolder).closest(".pathway-sub-folder");
                }
                else {
                    //folder doesn't exist, so create it
                    var thisModel = new Backbone.Model({name: folders[i]});
                    var thisRow = new FolderRow({model: thisModel, parentList: folders.slice(0,i)})
                    currentEl.append(thisRow.render().$el);
                    currentEl = $(thisRow.el);
                }
            }
        }
        var thisModel = new Backbone.Model({id: model.get('pathid'), name: model.get('name')})
        var pathRow = new PathRow({model: thisModel})

        $(currentEl).append(pathRow.render().$el)
        if (newlyAdded) {
            //open folder if this has been added by the user
            $(currentEl).children().css("display", "inline-block");
            if ($(currentEl)!=$("#avail-paths-list")){
                $(currentEl).children(".pathway-folder-title").children(".folder-state").switchClass("glyphicon-folder-close", "glyphicon-folder-open");
            }
        }
        //$('.sortable-folder').sortable("refresh");
        //return $(currentEl);
    },
	render: function(){
        var that = this;
        this.$el.html(this.template());
        var appendEl =  $('#avail-paths-list', this.$el)
        /*$.each(curCollection.folders, (function(folderName, children){
            that.renderFolder(folderName, children, $("#pathway-directory"), that);
        }));*/
        _.each(curCollection.models, function(cur){
            //var thisModel = new Backbone.Model({id: cur.get('pathid'), name: cur.get('name')})
            //var thisRow = new PathRow({model: thisModel})
            that.insertPathway(cur, false);
            //$(appendEl).append(thisRow.render().$el)
        }, this)
/*
        $('.sortable-folder').sortable({
            connectWith:    '.sortable-folder',
            cursor:         'move',
            placeholder:    'sortable-placeholder',
            tolerance:      'pointer',
            scroll:         false,
            handel:         'ui-state-default',
            zIndex:         9999,
        });
        $('.sortable-folder').disableSelection();*/

        $('.sortable-folder').sortable({
            connectWith: ".sortable-folder",
            items: '> div:not(.pathway-folder-title)', //don't allow user to move the folder title
            helper : 'clone',
            containment: "parent",
            sort: function (event, ui) {
                //make the sort function more responsive and user friendly
                //var that = $(this),
                var that = $(this);//ui.placeholder.parent();
                var w = ui.helper.outerHeight();
                that.children().each(function () {
                    if ($(this).hasClass('ui-sortable-helper') || $(this).hasClass('ui-sortable-placeholder'))
                        return true;
                    // If overlap is more than half of the dragged item
                    var dist = Math.abs(ui.position.top - $(this).position().top),
                        before = ui.position.top > $(this).position().top;
                    if ((w - dist) > (w / 2) && (dist < w)) {
                        if (before)
                            $('.ui-sortable-placeholder', that).insertBefore($(this));
                        else
                            $('.ui-sortable-placeholder', that).insertAfter($(this));
                        return false;
                    }
                });
            },
            receive: function(event, ui) {
                /*//if moving to a new folder, make sure the new folder is open and that items are visible
                folder = $(event.target).closest(".pathway-sub-folder");
                if (folder){
                    if (folder.find(".folder-state").hasClass("glyphicon-folder-close")) {
                        folder.find(".folder-state").switchClass("glyphicon-folder-close", "glyphicon-folder-open");
                    }
                    folder.find(".ui-state-default").css("display","inline-block");
                }
                else {
                    $(event.target).closest("display", "inline-block");
                }*/
            }
        });

    },
    handle_new_folder: function() {
        a = new newPathwayFolder({el: '#modal-target'});
    },
        handle_newPath: function () {
            a = new NewPathway({el: '#modal-target'});

        },
        handle_save: function(){
            curTree.save()
        }
    });
    return PathwaysList;
});
