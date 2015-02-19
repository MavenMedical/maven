/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani', 'Carlos Brenneisen'
 * DESCRIPTION: This file controls all of the events for the Pathway Manager.
 *              Events for individual Pathways, Folders, and History Items
 *              are handled by separate JS files for those specific objects
 **************************************************************************/

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
    'globalmodels/sidebarModel',

], function ($, _, Backbone,  contextModel, curCollection, curTree,  NewPathway, PathRow, pathwaysListTemplate, newPathwayFolder, FolderRow, sidebarModel) {

    var PathwaysList = Backbone.View.extend({
        template: _.template(pathwaysListTemplate),
        events: {
            'click #add-base-pathway': 'handle_newPath',
            'click #save-button': 'handle_save',
            'click #paths-list-add-folder': 'handle_new_folder',
            'change .mvn-importpath': 'importPathway'
        },
        initialize: function(){
            contextModel.on('change:page', function () {
                    if (contextModel.get('page') != 'pathEditor') {
                        this.$el.hide()
                    } else {
                        this.$el.show()
                    }
                }, this)
                sidebarModel.addOption('Pathway Mgmt')

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
        importPathway: function(){
            var input = $('.mvn-importpath')
            file = input.get(0).files[0];
            if (file) {
                var reader = new FileReader();
                reader.readAsText(file, "UTF-8");
                reader.onload = function (evt) {
                    try{
                        var importedPath = JSON.parse(evt.target.result);
                        curTree.loadNewPathway(importedPath, {toImport: true})
                    }
                    catch(e){
                        alert("The format of the file doesn't match Pathway format. Please try another file");
                    }

                }
                reader.onerror = function (evt) {
                    alert('error reading file')
                }
                input.wrap('<form>').closest('form').get(0).reset();
                input.unwrap();
            }
        },
        insertPathway: function(model, newlyAdded){
            //given a pathway's location, add it to the proper folder; if folder doesn't exist, create it

            var currentEl = $("#avail-paths-list");
            var path = model.get('folder');

            if (path!=null && path!="") {
                //if path isn't specified, simply add pathway to the top level

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
                //select the pathway if this has been added by the user
                pathRow.handleSelect();

                if (path!=null && path!="") {
                    //if added to a folder, make sure its open
                    var parentFolder = $(currentEl).closest(".sub-folder");
                    if (parentFolder.hasClass("dd-collapsed")) {
                        parentFolder.children(".show-hist").click();
                    }
                }

                pathRow.$el.prepend("<button data-action='collapse' title='Collapse' style='display:none;'>collapse</button>");
                pathRow.$el.prepend("<button data-action='expand' title='Expand' class='show-hist'>expand</button>");
            }
        },
        render: function(){
            var that = this;
            this.$el.html(this.template());                    
            if (contextModel.get('page') != 'pathEditor') {
                this.$el.hide()
            }

            _.each(curCollection.models, function(cur){
                that.insertPathway(cur, false);
            }, this)

            curCollection.makeSortable();

            $(this.el).on("change", function(event){
                event.stopPropagation();
                that.handleChange($("#avail-paths-list"), "", that);
            })
        },
        handle_new_folder: function() {
            a = new newPathwayFolder({el: '#modal-target'});
        },
        handle_newPath: function () {
            a = new NewPathway({el: '#modal-target'});
        },
        handle_save: function(){
            curTree.save()
        },
        handleMovedPath: function(canonical_id, locationData){
            //update order
            var data = {'canonical': canonical_id, 'customer_id': contextModel.get("customer_id"), 'userid': contextModel.get("userid")}
            $.extend(data, contextModel.toParams(), data);
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: "/update_pathway_location?" + $.param(data),
                data: JSON.stringify(locationData),
                success: function () {
                    console.log("pathway location updated");
                }
            });
        },
        handleChange: function(folder, path, that){
            var position = 0;
            $(folder).children().each(function(){
                if ($(this).hasClass("pathrow-item")){
                    //update order
                    position++;
                    var locationData = { "location": path, "position": position}
                    var canonical_id = $(".path-row", $(this)).attr("id");
                    that.handleMovedPath(canonical_id, locationData)
                }
            });
        },
    });
    return PathwaysList;
});
