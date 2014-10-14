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
    tried: 0,
    offset: 0,
	model: ScrollModel,
    data: "",
    lastRefresh: new Date(),
    getLastRefresh: function() {
        //returns the formatted version of the last time this collection was refreshed/initialized
        return this.lastRefresh.toISOString().replace("T", " ").substr(0,19);
    },
    context: function(){
        //context change listener - this will need to be defined by the subclass
    },
    initialize: function(){
        this.tried = 0;
        this.offset = 0;
        if(contextModel.get('userAuth') && this.url) {
            //allow for additional data to be passed in, aside from the context model
            if (this.data != "")
            {
                data = $.param(contextModel.toParams()) + "&" + this.data;
            }
            else
            {
                data = $.param(contextModel.toParams());
            }
            this.fetch({data:data, remove:true});
	    }

        //setup context change listener
        this.context();
    },
    more: function() {
	    if(this.tried <= this.models.length) {
            //allow for additional data to be passed in, aside from the context model
                data = $.param(contextModel.toParams());
		if (this.data != "")
		{
                    data += "&" + this.data;
		}
		if (this.extraData) {
		    data += this.extraData;
		}
            this.offset = this.models.length;
            this.tried = this.models.length+this.limit;
            this.fetch({
                data:data,
                remove:false
            });
            }
	    },
    });

    return ScrollCollection;
});
