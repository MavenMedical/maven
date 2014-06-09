
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/contextModel',

    'text!templates/detailPanel/detailChooserEntry.html'
], function ($, _, Backbone, contextModel, detailEntry) {

    var DetailSelector = Backbone.View.extend({

        template: _.template(detailEntry),
        initialize: function(){
            alert("inti")
            var panel = this;
            var anon =  Backbone.Collection.extend( {url: '/details?'});
            var searchedDetailTypes = new anon();
            searchedDetailTypes.fetch({data:$.param(contextModel.toParams()), success: function(data){
                console.log(data);
                panel.availTypes = searchedDetailTypes;
                console.log(searchedDetailTypes);
                panel.render();
            }
            });



        },
        render: function(){
            this.$el.html("");
            _.each (this.availTypes.models, function(cur) {
                console.log(cur);
                this.$el.append(this.template(cur.toJSON));


            } , this);
            return this;

        }

    });

    return DetailSelector;

});
