/**
 * Created by Asmaa Aljuhani on 7/23/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
], function ($, _, Backbone, contextModel) {

    var Profile = Backbone.View.extend({
            initialize: function(arg){
                this.template = _.template(arg.template);
                this.render();
            },
            render: function (){
                this.$el.html(this.template(contextModel.attributes));
            }
    });
    return Profile;

});
