/**
 * Created by Asmaa Aljuhani on 10/7/14.
 */


define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
], function ($, _, Backbone, contextModel) {

    var Welcome = Backbone.View.extend({
            initialize: function(arg){
                console.log('welcome',contextModel.attributes );
                this.template = _.template(arg.template);
                this.render();
            },
            render: function (){
                this.$el.html(this.template(contextModel.attributes));
            }

    });
    return Welcome;

});
