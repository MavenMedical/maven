
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',

    'text!templates/individualDetails/detailSearch.html',
    'text!templates/triggerSelector/triggerSelectorRow.html'
], function ($, _, Backbone, contextModel, detailSearch, triggerSelectorRow) {
    var DetailSearchBox = Backbone.View.extend({

        initialize: function(params){

            this.template= _.template(detailSearch);
                 this.$el.html(this.template());
            this.collection  = params.collection;
            this.el = params.el;
            this.type = params.type;
            this.collection.on('sync', this.render, this);
            console.log($('#searchButton', this.$el));
            var panel = this;
            $('#searchButton', this.$el)[0].onclick = function(){

                var t = contextModel.toParams();
                $.extend( t, {'search_param': $('#Detail-Search-Box').val()})
                $.extend( t, {'type': panel.type});

             panel.collection.fetch({data:$.param(t)})
            }
        },
        render: function(){

               $('.entries', this.$el).html("");
              var entryview = Backbone.View.extend({
                    template: _.template(triggerSelectorRow),
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

    return DetailSearchBox;

});
