/**
 * Created by Asmaa Aljuhani on 1/21/15.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
      'pathway/models/pathwayCollection',
    'text!templates/pathway/deletePathModal.html'
], function ($, _, Backbone, pathwayCollection, deletePathTemplate) {
    var DeletePath = Backbone.View.extend({
        template: _.template(deletePathTemplate),
        elModel: null,
        elToDelete: null,
        events:{
            'click #deletePathway' : 'deletePathway'
        },
        initialize: function (params){
            this.$el.html(this.template());
            this.elModel = params.elModel;
            this.elToDelete = params.elToDelete;
            $("#delete-pathway-modal").modal({'show':'true'});
        },
        deletePathway: function(){
             this.elModel.destroy({success: function(){
                 pathwayCollection.fetch();
             }})
            $(this.elToDelete).remove();

            $("#delete-pathway-modal").modal('hide');
        }
    });
    return DeletePath;


});