
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/Helpers',
    'pathway/internalViews/detailSearchBox',
    'pathway/internalViews/multiSelectSearch',

    'text!templates/pathway/triggerEditor.html'
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
            })
            $('.cancel-edit-button', this.$el).on('click', function(){
                $('#detail-modal').modal('hide')
            })
            $('#confirmDetailButton', this.$el).on('click', function(){
                alert()

                _.each(panel.searchBox.selected_items.models, function(cur){

                    if (!panel.triggerNode.get('triggers')){
                        panel.triggerNode.set({triggers: new Backbone.Collection()}, {silent: true})

                    }
                    cur.set('exists', $('#existsField').val());
                    console.log(panel.triggerNode)
                    panel.triggerNode.get('triggers').add(cur)

                })
                $('#detail-modal').modal('hide')


            })
        },
        render: function(){

             $("#detail-modal").modal({'show':'true'});
         }
    })

    return DetailEditor;

});
