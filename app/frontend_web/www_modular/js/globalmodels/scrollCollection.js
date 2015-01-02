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
    url: null,
    limit: 10,
    offset: 0,
    model: ScrollModel,
    extraData: {},
    lastRefresh: new Date(),
    getLastRefresh: function() {
        //returns the formatted version of the last time this collection was refreshed/initialized
        return this.lastRefresh.toISOString().replace("T", " ").substr(0,19);
    },
    context: function(){
        //context change listener - this will need to be defined by the subclass
    },
    initialize: function(){
        this.offset = 0;
        if(contextModel.get('userAuth') && this.url) {
            //allow for additional data to be passed in, aside from the context model
            var data = {};
            $.extend(data,contextModel.toParams(),this.extraData);
            this.active=1
            var that = this
            this.fetch({
                data: $.param(data), remove:true,
                success: function(res) {that.full = res.length < that.limit; that.active=0},
                error: function() {that.full = 1; that.active=0}
            });
            
	    }

        //setup context change listener
        this.context();
    },
    more: function() {
	if(!this.full && !this.active) {
            //allow for additional data to be passed in, aside from the context model
            var data = {};
            $.extend(data,contextModel.toParams(),this.extraData);
            var that=this
            this.offset = this.models.length;
            this.active=1
            this.fetch({
                data: $.param(data),
                remove:false,
                success: function(res) {that.active=0;that.full = res.length < that.limit},
                error: function() {that.full = 1;that.active=0}
            });
        }
	}
    });

    return ScrollCollection;
});
