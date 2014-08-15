/* a backbone view for representing a single select list box for picking a cpt proc or snomed concept for use by a detail,
   it is not used currently, as all details use the multiSelectSearch instead

  */
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


        doSearch: function(panel){

                var t = contextModel.toParams();
                $.extend( t, {'search_param': $('#Detail-Search-Box').val()})
                var ty = panel.type.split("_");
                if (ty[ty.length-1] == 'dx'){
                     $.extend( t, {'type': "snomed_diagnosis"})
                } else if (panel.type.split("_")[1] == 'NDC' || panel.type.split("_")[1] == 'med'){
                   $.extend( t, {'type': "snomed_drug"});
                } else if (panel.type.split("_")[1] == 'proc'){
                   $.extend( t, {'type': "CPT"});
                }
                this.collection.fetch({data:$.param(t), success:function(){
                    if (panel.collection.length>0 &&panel.collection.models[0].get('type')!='none'){
                        panel.ready = true;
                    }

                }})

        },

        initialize: function(params){
            this.template= _.template(detailSearch);
                 this.$el.html(this.template());
            this.collection  = params.collection;


            if (this.collection.length==0) {
                this.ready = false;
            } else {
                this.ready = true
            }

            this.collection.on('add', function(){
                this.ready = true
            }, this)

            this.el = params.el;
            this.type = params.type;
            this.collection.on('sync', this.render, this);

            var panel = this;
            $('#searchButton', this.$el)[0].onclick = function(){
                 panel.doSearch(panel)

            }
            $('#zoom-in-button', this.$el)[0].on = function(){
                var t = contextModel.toParams();
                $.extend( t, {'search_param': $('#search_results').val()})
                $.extend( t, {'type': "snomed_zoom_in"})

                panel.collection.fetch({data:$.param(t)})



            }
            $('#zoom-out-button', this.$el)[0].onclick = function(){
                var t = contextModel.toParams();
                $.extend( t, {'search_param': $('#search_results').val()})
                $.extend( t, {'type': "snomed_zoom_out"})

                panel.collection.fetch({data:$.param(t)})



            }
             $('#Detail-Search-Box', this.$el)[0].onkeydown = function(key){

                if (key.keyCode == 13){
                    panel.doSearch(panel)
                }
             }
        },


        render: function(){

               $('.entries', this.$el).html("");
               var entryview = Backbone.View.extend({
                    template: _.template(triggerSelectorRow),
                    render: function(){
                        if (!this.model.get('route')){
                            this.model.set('route', "")
                        }
                        this.model.set('id', this.model.get('code')+this.model.get('route'))
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
