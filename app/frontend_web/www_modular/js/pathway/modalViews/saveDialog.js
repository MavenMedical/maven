define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/treeModel',
    'text!templates/pathway/saveModal.html'


], function ($, _, Backbone,   curTree, template) {

    var SaveDialog = Backbone.View.extend({
         template: _.template(template),
         el: '#modal-target',
         initialize: function() {
             return
             this.$el.html(this.template())
             $('#detail-modal').modal('show')
         },
        events: {
            'click #save': 'saveChanges',
            'click #dontsave' : 'dontSaveChanges'
        },
        saveChanges: function() {
            curTree.save();
            $('#detail-modal').modal('hide')
        },
        dontSaveChanges: function() {
            $('#detail-modal').modal('hide')
        }

    });
    return SaveDialog
});