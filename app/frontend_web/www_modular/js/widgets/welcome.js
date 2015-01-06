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
                this.showhide();
                contextModel.on('change:page', this.showhide , this)
		        contextModel.on('change:pathid', this.render, this);
            },
            render: function (){
            if (contextModel.get('pathid') && contextModel.get('pathid') > 0) {
                this.$el.hide();
            } else {
                this.$el.html(this.template(contextModel.attributes));
                this.showhide(); //$el.show();
		    }
            },
        showhide: function(){
            if(contextModel.get('page') == 'home'){
                this.$el.show();
            }else{
                this.$el.hide();
            }
        }


    });
    return Welcome;

});
