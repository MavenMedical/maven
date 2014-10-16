define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection',
    ''
], function($, _, Backbone, contextModel, ScrollCollection) {
    UserModel = Backbone.Model;

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
            /*extraData = "";
            if (userCollection.target_customer != ""){
                extraData = "target_customer=" + userCollection.target_customer;
                userCollection.data = extraData;
                extraData ="&" + extraData;
            }*/
            var data = {};
            $.extend(data,contextModel.toParams(),userCollection.extraData);
            /*if (this.data != "")
            {
                data += "&" + this.data;
            }*/
            this.tried = 0;
            this.offset = 0;
            userCollection.fetch({
            data:$.param(data),
        remove:true});
    }
    };
    return userCollection;
});
