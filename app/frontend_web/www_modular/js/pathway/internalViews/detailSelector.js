
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
   'globalmodels/contextModel',
    'pathway/Helpers',
    'text!templates/pathway/detailChooserEntry.html'
], function ($, _, Backbone, contextModel, Helpers, detailEntry) {

    var DetailSelector = Backbone.View.extend({
        initialize: function(param){
            this.el = param.el;
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
                this.$el.append(entryTemplate({id:cur.get('id'), desc:Helpers.detailDescriptions[cur.get('type')], type:Helpers.detailHeadings[cur.get('type')]}));

            }



        }
    })


    return DetailSelector;

});
