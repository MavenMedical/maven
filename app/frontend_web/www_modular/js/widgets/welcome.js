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
                this.template = _.template(arg.template);
                this.render();
		contextModel.on('change:pathid', this.render, this);
            },
            render: function (){
		if (contextModel.get('pathid') && contextModel.get('pathid') > 0) {
		    this.$el.hide();
		} else {
                    this.$el.html(this.template(contextModel.attributes));
		    this.$el.show();
		}
            }

    });
    return Welcome;

});
