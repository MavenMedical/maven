define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    InteractionModel = Backbone.Model;

    var InteractionCollection = ScrollCollection.extend({
        url: function() {return '/interactions'+this.offset+'-'+(this.offset+this.limit);},
        model: InteractionModel,
        limit: 10,
        context: function(){
            $(".interactionlist").on('show',
		    // make sure the correct interaction list is being loaded (user's own list versus target user)
		    this.fetch_refresh, this);
        },
    });

    return InteractionCollection;
});
