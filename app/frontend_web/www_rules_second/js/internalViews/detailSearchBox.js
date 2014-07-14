
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',

    'text!templates/individualDetails/detailSearch.html',
    'text!templates/SearchSelectorRow/triggerSelectorRow.html'
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
                if (panel.type.split("_")[1] == 'dx'){
                     $.extend( t, {'type': "snomed_diagnosis"});
                } else if (panel.type.split("_")[1] == 'NDC' || panel.type.split("_")[1] == 'med'){
                   $.extend( t, {'type': "snomed_drug"});
                } else if (panel.type.split("_")[1] == 'HCPCS'){
                   $.extend( t, {'type': "CPT"});
                }
                panel.collection.fetch({data:$.param(t)})
            }
            $('#zoom_button', this.$el)[0].onclick = function(){
                var t = contextModel.toParams();
                console.log($('#search_sesults').val())
                $.extend( t, {'search_param': $('#search_results').val()})
                $.extend( t, {'type': "snomed_zoom_in"});

                panel.collection.fetch({data:$.param(t)})



            }
             $('#Detail-Search-Box', this.$el)[0].onkeydown = function(key){

                if (key.keyCode == 13){
                      var t = contextModel.toParams();
                $.extend( t, {'search_param': $('#Detail-Search-Box').val()})
                if (panel.type.split("_")[1] == 'dx'){
                     $.extend( t, {'type': "snomed_diagnosis"});
                } else if (panel.type.split("_")[1] == 'NDC' || panel.type.split("_")[1] == 'med'){
                   $.extend( t, {'type': "snomed_drug"});
                } else if (panel.type.split("_")[1] == 'HCPCS'){
                   $.extend( t, {'type': "CPT"});
                }
                panel.collection.fetch({data:$.param(t)})
                }
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
