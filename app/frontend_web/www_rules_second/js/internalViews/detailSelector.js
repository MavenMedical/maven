
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/contextModel',


    'Helpers',
    'text!templates/detailPanel/detailChooserEntry.html'
], function ($, _, Backbone, contextModel, Helpers, detailEntry) {

    var DetailSelector = Backbone.View.extend({
        template: _.template(detailEntry),
        initialize: function(param){
            this.el = param.el;
            console.log(this.$el);
            var anon =  Backbone.Collection.extend( {url: '/details?'});
            this.searchedDetails = new anon();
            contextModel.on('change:auth', this.other, this);

        },
        other:function(){
            this.search("")
        },
        search: function(search_param){
            var panel = this;
            var t = contextModel.toParams();
            console.log(t);
            t = $.extend(t , {'search_param': search_param});
            this.searchedDetails.fetch({data:$.param(t), success:function(){
                 panel.render();
            }})

        },
        render: function(){
            this.$el.html("");
            var entryTemplate = _.template(detailEntry);
            for (var i in this.searchedDetails.models){
                var cur = this.searchedDetails.models[i]
                this.$el.append(entryTemplate({id:cur.get('id'), type:Helpers.detailHeadings[cur.get('type')]}));

            }



        }
    })


    return DetailSelector;

});
