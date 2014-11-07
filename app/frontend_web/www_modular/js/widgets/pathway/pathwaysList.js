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

], function ($, _, Backbone,  curCollection, curTree,  NewPathway, PathRow, pathwaysListTemplate, newPathwayFolder) {

    var PathwaysList = Backbone.View.extend({
        template: _.template(pathwaysListTemplate),
         events: {
            'click #newpath-button': 'handle_newPath',
            'click #save-button': 'handle_save',
            'click #paths-list-add-folder': 'handle_new_folder'
        },
	initialize: function(){
	    curCollection.on('sync',this.render, this)
        this.render();

	},
	render: function(){
        this.$el.html(this.template());
        var appendEl =  $('#avail-paths-list', this.$el)
        _.each(curCollection.models, function(cur){
            var thisModel = new Backbone.Model({id: cur.get('pathid'), name: cur.get('name')})
            var thisRow = new PathRow({model: thisModel})
            appendEl.append(thisRow.render().$el)
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
        new newPathwayFolder(this.model);
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
