/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */


define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'pathway/models/treeModel',

    'text!templates/pathway/newPathway.html'
], function ($, _, Backbone, curTree, newPathwayTemplate) {
    var NewPathway = Backbone.View.extend({
        template: _.template(newPathwayTemplate),
        parentList: "",
        parentFolder: null,
        events: {
            'click #create-button': 'handle_createPathway'
        },
        initialize: function (params) {

            if (typeof params.parentList !== 'undefined'){
                this.parentList = "/" + params.parentList.join("/");
            }
                        if (typeof params.parentFolder !== "undefined") {
                this.parentFolder = params.parentFolder;
            }

            this.$el.html(this.template());
            //$('#create-button', this.$el).on('click',this.handle_createPathway)
            $("#newpathwaymodal").modal({'show':'true'});
        },
        handle_createPathway: function(){
            //hide modal
            $("#newpathwaymodal").modal('hide');
            curTree.loadNewPathway({name: $('#newPathName').val(), folder: this.parentList, parentFolder: this.parentFolder});

            this.undelegateEvents(); // Unbind all local event bindings

            delete this.$el; // Delete the jQuery wrapped object variable
            delete this.el; // Delete the variable reference to this node
        }
    });
    return NewPathway;

});
