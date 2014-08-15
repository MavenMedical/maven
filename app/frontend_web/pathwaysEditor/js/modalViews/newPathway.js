/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */


define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/treeModel',

    'text!templates/newPathway.html'
], function ($, _, Backbone, curTree, newPathwayTemplate) {
    var NewPathway = Backbone.View.extend({
        template: _.template(newPathwayTemplate),
        initialize: function () {
            this.$el.html(this.template());
             $('#create-button', this.$el).on('click',this.handle_createPathway)
        },

        handle_createPathway: function(){
            //hide modal
            $("#createNewPath-modal").modal('hide');
            curTree.loadNewPathway({name: $('#newPathName').val()});

        }
    });
    return NewPathway;

});
