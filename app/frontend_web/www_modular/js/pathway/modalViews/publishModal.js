/**
 * Created by Asmaa Aljuhani on 1/21/15.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
       'globalmodels/contextModel',
        'pathway/models/treeModel',
    'text!templates/pathway/publishModal.html'
], function ($, _, Backbone, contextModel, curTree, publishTemplate) {
    var PublishPath = Backbone.View.extend({
        template: _.template(publishTemplate),
        events:{
            'click #publishPathway' : 'publishPathway'
        },
        initialize: function (params){
            this.$el.html(this.template());
            $("#publish-pathway-modal").modal({'show':'true'});
        },
        publishPathway: function(){
            $.ajax({
                type: 'POST',
                url: "/history/"  + contextModel.get("canonical") + "/" + curTree.get('pathid'),
                dataType: "json",
                success: function (data) {
                    console.log("Pathway version published");
                }
            });

            $("#publish-pathway-modal").modal('hide');
        }
    });
    return PublishPath;


});