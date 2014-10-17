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
		    this.refresh);
        },
        refresh: function() {
            if (contextModel.get('userAuth')) {
                //allow for additional data to be passed in, aside from the context model
                var data = {};
                $.extend(data, contextModel.toParams(), this.extraData);

                this.tried = 0;
                this.offset = 0;
                userCollection.fetch({
                    data: $.param(data),
                    remove: true});
            }
        }
    });
    return UserCollection;

/*
    userCollection = new ScrollCollection;
    userCollection.url = function() {return '/users'+this.offset+'-'+(this.offset+this.limit);};
    userCollection.model = UserModel;
    userCollection.limit = 10;
    userCollection.target_customer = "";
    userCollection.extraData = {};
    userCollection.context = function(){
        contextModel.on('change:startdate change:enddate',
		    // this will be needed once the context filters things
		    userCollection.refresh);
    };

    userCollection.initialize();
    userCollection.refresh = function() {
        if(contextModel.get('userAuth')) {
            userCollection.extraData = "";
            if (userCollection.target_customer != ""){
                userCollection.extraData = "&target_customer=" + userCollection.target_customer;
            }

            userCollection.tried = 0;
            userCollection.offset = 0;
	    userCollection.reset();
            userCollection.more();
	}
    };
            //allow for additional data to be passed in, aside from the context model
            var data = {};
            $.extend(data,contextModel.toParams(),userCollection.extraData);

            this.tried = 0;
            this.offset = 0;
            userCollection.fetch({
            data:$.param(data),
        remove:true});
    }
    };*/
});
