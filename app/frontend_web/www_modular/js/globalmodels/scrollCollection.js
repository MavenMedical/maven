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
    full: 1,
    model: ScrollModel,
    extraData: {},
    lastRefresh: new Date(),
    getLastRefresh: function() {
        //returns the formatted version of the last time this collection was refreshed/initialized
        return String(this.lastRefresh).substr(0, String(this.lastRefresh).indexOf(' GMT'));//.toISOString().replace("T", " ").substr(0,19);
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
                success: function(fulcol, res) {that.full = res.length < that.limit; that.active=0},
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
                success: function(fullcol, res) {that.active=0;that.full = res.length < that.limit},
                error: function() {that.full = 1;that.active=0}
            });
        }
	},
    refresh: function() {this.fetch_refresh()},
    fetch_refresh: function() {
        if (contextModel.get('userAuth')) {
            
            var data = {};
            $.extend(data, contextModel.toParams(), this.extraData);
            
            this.offset = 0;
            this.full = 0;
            this.active = 1;
            var that=this
            this.fetch({
                data: $.param(data),
                remove: true,
                success: function(fullcol, res) {
                    that.full = res.length < that.limit; that.active=0;
                    that.set({lastRefresh: new Date()});
                },
                error: function() {that.full = 1; that.active=0}
            });
        }
    },
    });

    return ScrollCollection;
});
