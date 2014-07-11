
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',

    'text!templates/individualDetails/routeList.html',
    'text!templates/SearchSelectorRow/drug_route.html'
], function ($, _, Backbone, contextModel, routeList, drugRouteRow) {
    var routeListBox = Backbone.View.extend({

        initialize: function(params){

            this.template= _.template(routeList);
            this.$el.html(this.template());
            var route_collection = Backbone.Collection.extend({url: "/routes"})
            this.el = params.el;

            this.collection  = new route_collection();

            this.collection.on('sync', this.render, this);
            this.collection.fetch({data:$.param(contextModel.toParams())});

        },
        render: function(){
               $('.entries', this.$el).html("");
               var entryview = Backbone.View.extend({
                    template: _.template(drugRouteRow),
                    render: function(){
                        this.$el.html(this.template(this.model.toJSON()));
                        return this;
                    }
                });
            _.each(this.collection.models, function(cur){
                var curentry = new entryview({model: cur});
                $('.entries', this.$el).append(curentry.render().el.innerHTML);

            }, this);
            return this;
        }
    });

    return routeListBox;

});
