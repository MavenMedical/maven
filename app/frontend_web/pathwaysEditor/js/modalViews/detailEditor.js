
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'Helpers',
    'internalViews/detailSearchBox',
    'internalViews/multiSelectSearch',

    'text!templates/triggerEditor.html'
], function ($, _, Backbone, Helpers, detailSearchBox, multiSelectSearch, editorTemplate) {

    var DetailEditor = Backbone.View.extend({
         template: _.template(editorTemplate),
         el: '#modal-target',
        initialize: function(param){
            this.triggerNode = param.triggerNode
            this.$el.html(this.template())
            var multiSearchEl = $('.multi-select-search', this.$el)
            var panel = this
            $.each(multiSearchEl, function(a, cur){
                var anon =  Backbone.Collection.extend( {url: '/search'})
                var sel = new Backbone.Collection

                panel.searchBox = new multiSelectSearch({avail: new anon(), type: cur.getAttribute("type"), el: multiSearchEl, selected: sel})
                console.log(panel)
            })
            $('.cancel-edit-button', this.$el).on('click', function(){
                $('#detail-modal').modal('hide')
            })
            $('.confirm-detail-button', this.$el).on('click', function(){
                _.each(panel.searchBox.selected_items.models, function(cur){
                    console.log(cur)
                    if (!panel.triggerNode.get('triggers')){
                        panel.triggerNode.set({triggers: new Backbone.Collection()}, {silent: true})
                    }
                    panel.triggerNode.get('triggers').add(cur)

                })


            })
        },
        render: function(){

             $("#detail-modal").modal({'show':'true'});
         }
    })

    return DetailEditor;

});
