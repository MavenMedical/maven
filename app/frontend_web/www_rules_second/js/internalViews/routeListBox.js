/* a Backbone View displaying a list of all of the routes for drugs, to be used by triggers and details
   the set of items is fetched from the server

    params:
        el      : the location in which to render the list

  */
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
            //load the parameter
            this.el = params.el;

            //the collection object in this view has the url /routes and can be feteched from the server
            var route_collection = Backbone.Collection.extend({url: "/routes"})
            this.collection  = new route_collection();
            //when data is recieved from the server re-render the routes
            this.collection.on('sync', this.render, this);

            //fetch the data from the server
            this.collection.fetch({data:$.param(contextModel.toParams())});

        },
        render: function(){
               $('.entries', this.$el).html("<option value = '%' selected>ANY ROUTE</option> ");
               var entryview = Backbone.View.extend({
                    template: _.template(drugRouteRow),
                    render: function(){
                        this.$el.html(this.template(this.model.toJSON()));
                        return this;
                    }
                });
            _.each(this.collection.models, function(cur){
                var curentry = new entryview({model: cur});
                $('.entries', this.$el).append(curentry.render().$el);

            }, this);

            return this;
        }
    });

    return routeListBox;

});
