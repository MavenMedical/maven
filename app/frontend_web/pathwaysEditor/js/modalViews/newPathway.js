/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */


define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'text!templates/newPathway.html'
], function ($, _, Backbone, newPathwayTemplate) {
    var NewPathway = Backbone.View.extend({
        template: _.template(newPathwayTemplate),
        events:{
          'click #create-button' : 'handle_createPathway'
        },
        initialize: function () {
            this.render();
        },
        render: function () {
            this.$el.html(this.template());
        },
        handle_createPathway: function(){
            //hide modal
            $("#createNewPath-modal").modal('hide');
            //navigate to new pathway page
            Backbone.history.navigate('createpathway', {trigger: true});
        }
    });
    return NewPathway;

});
