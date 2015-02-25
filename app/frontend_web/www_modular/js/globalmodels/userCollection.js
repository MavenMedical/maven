define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection',
], function($, _, Backbone, contextModel, ScrollCollection) {
    UserModel = Backbone.Model;

    var UserCollection = ScrollCollection.extend({
        url: function () {return '/users' + this.offset + '-' + (this.offset + this.limit);},
        model: UserModel,
        context: function(){
            contextModel.on('change:startdate change:enddate',
		    // this will be needed once the context filters things
		    this.refresh, this);
        },
    });
    return UserCollection;
});
