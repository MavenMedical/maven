define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbones
    'pathway/models/pathwayCollection',

    'text!templates/pathway/newPathwayFolder.html',

], function ($, _, Backbone, curCollection, newPathwayFolderTemplate) {

   var FolderRow;

    var NewPathwayFolder = Backbone.View.extend({
        template: _.template(newPathwayFolderTemplate),
        parentList: [],
        parentFolder: null,
        events: {
            'click .createPathwayFolder': 'handleCreateFolder',
        },
        initialize: function (arg) {
            FolderRow = require('pathway/singleRows/folderRow');
            if (typeof arg.parentFolder !== "undefined") {
                this.parentFolder = arg.parentFolder;
            }
            if (typeof arg.parentList !== "undefined") {
                this.parentList = arg.parentList;
            }

            //var that = this;
            //this.parent = parent;
            this.$el.html(this.template(this.attributes));
            $("#detail-modal").modal({'show': 'true'});
            //$(".createPathwayFolder", this.$el).on("click", this.handleCreateFolder);
        },
        handleCreateFolder: function(){
            $('#detail-modal').modal('hide');

            var folder_name = $(".pathwayFolderName", this.$el).val();
            var thisModel = new Backbone.Model({name: folder_name});
            var thisRow = new FolderRow({model: thisModel, parentList: this.parentList})

            if (this.parentFolder !== null) {
                //add folder
                this.parentFolder.append(thisRow.render().$el);

                //open parent folder
                //$(".folder-state", this.parentFolder).switchClass("glyphicon-folder-close", "glyphicon-folder-open");
                 //$(".ui-state-default", this.$el).css("display","inline-block");
                    //thisRow.$el.siblings().css("display","inline-block");
            }
            else {
                $("#avail-paths-list").append(thisRow.render().$el);
            }
            $(document).ready(function() {
               // curCollection.makeSortable();
                $(thisRow.el).removeClass("dd-collapsed");
            });

            this.undelegateEvents(); // Unbind all local event bindings

            delete this.$el; // Delete the jQuery wrapped object variable
            delete this.el; // Delete the variable reference to this node

        }
    });
    return NewPathwayFolder;
});
