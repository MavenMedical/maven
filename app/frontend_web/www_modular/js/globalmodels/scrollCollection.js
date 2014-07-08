/**
 * Created by devel on 7/1/14.
 */

define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function ScrollCollection($, _, Backbone, contextModel) {
    ScrollModel = Backbone.Model;

    var ScrollCollection = Backbone.Collection.extend({
    url: function() {return '//';},
    limit: 3,
    tried: 0,
    offset: 0,
	model: ScrollModel,
    context: function(){

        //context change listener - this will need to be defined by the subclass
    },
	initialize: function(){

        if(contextModel.get('userAuth')) {

        this.tried = 0;
        this.offset = 0;
        this.fetch({
            data:$.param(contextModel.toParams()),
            remove:true});
        }

        //setup context change listener
        this.context();
    },
    more: function() {
	    if(this.tried <= this.models.length) {
            this.offset = this.models.length;
            this.tried = this.models.length+this.limit;
            this.fetch({
                data:$.param(contextModel.toParams()),
                remove:false});
            }
	    },
    });

    return ScrollCollection;
});
