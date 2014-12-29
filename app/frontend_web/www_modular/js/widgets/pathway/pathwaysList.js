/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',

    'pathway/models/pathwayCollection',
    'pathway/models/treeModel',
    'pathway/modalViews/newPathway',

    'pathway/singleRows/pathRow',
    'text!templates/pathway/pathwaysList.html',

    'pathway/modalViews/newPathwayFolder',
    'pathway/singleRows/folderRow',
    'widgets/pageOption',

], function ($, _, Backbone,  contextModel, curCollection, curTree,  NewPathway, PathRow, pathwaysListTemplate, newPathwayFolder, FolderRow, pageOption) {

    var PathwaysList = Backbone.View.extend({
        template: _.template(pathwaysListTemplate),
        events: {
            //'click #newpath-button': 'handle_newPath',
            'click #add-base-pathway': 'handle_newPath',
            'click #save-button': 'handle_save',
            'click #paths-list-add-folder': 'handle_new_folder'
        },
	initialize: function(){
        contextModel.on('change:page', function () {
                if (contextModel.get('page') != 'pathEditor') {
                    this.$el.hide()
                } else {
                    this.$el.show()
                }
            }, this)
        new pageOption({'Pathway Mgmt': ['fa-cloud', 'pathway', [
                    {'Pathway Viewer': ['icon', 'pathway']},
                    {'Pathway Editor': ['icon', 'pathwayEditor']}
                ]]});
	    //curCollection.on('sync', this.render, this)
        curCollection.bind('add', this.addNewPathway, this);

        this.render();
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

        var currentEl = $("#avail-paths-list");
        var path = model.get('folder');

        //if path isn't specified, simply add pathway to the top level
        if (path!=null && path!="") {
            var folders = path.split('/');

            for (var i = 0; i < folders.length; i++) {
                var foundFolder = false;
                $.each(currentEl.children("li"), function () {
                    var title = $(this).children(".pathway-folder-title").attr("name");
                    if (title) {
                        if (title == folders[i]) {
                            currentEl = $(this).children("ol");
                            foundFolder = true;
                            return false;
                        }
                    }
                });
                if (foundFolder) {
                    //folder exists
                    continue;
                }
                else {
                    //folder doesn't exist, so create it
                    var thisModel = new Backbone.Model({name: folders[i]});
                    var thisRow = new FolderRow({model: thisModel, parentList: folders.slice(0,i)})
                    var lastFolder = currentEl.children('.sub-folder').last();
                    if (lastFolder.length){
                        $(thisRow.render().$el).insertAfter(lastFolder);
                    }
                    else {
                        currentEl.prepend(thisRow.render().$el);
                    }
                    currentEl = $(thisRow.el).children("ol");
                }
            }
        }
        //create new pathway row
        var thisModel = new Backbone.Model({id: model.get('pathid'), name: model.get('name'), canonical: model.get("canonical"), enabled: model.get("enabled")})
        var pathRow = new PathRow({model: thisModel})

        $(currentEl).append(pathRow.render().$el)
        if (newlyAdded) {
            //open folder and select the pathway if this has been added by the user
            pathRow.handleSelect();
            $(currentEl).closest("li").switchClass("mjs-nestedSortable-collapsed", "mjs-nestedSortable-expanded");
        }
    },
	render: function(){
        var that = this;
        this.$el.html(this.template());
        var appendEl =  $('#avail-paths-list', this.$el)

        _.each(curCollection.models, function(cur){
            that.insertPathway(cur, false);
        }, this)

        curCollection.makeSortable();

    },
    handle_new_folder: function() {
        a = new newPathwayFolder({el: '#modal-target'});
    },
        handle_newPath: function () {
         //   a = new NewPathway({el: '#modal-target'});
            a = new NewPathway({el: '#modal-target'});
        },
        handle_save: function(){
            curTree.save()
        }
    });
    return PathwaysList;
});
