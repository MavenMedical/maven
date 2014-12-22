
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
        //replace this load with one which will take a parameter template
        template: _.template(editorTemplate),
         el: '#detailed-trigger-modal',
        initialize: function(param){
            this.triggerNode = param.triggerNode
            //replace this load with one which will take a parameter template
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

                _.each(panel.searchBox.selected_items.models, function(cur){

                    if (!panel.triggerNode.get('triggers')){
                        panel.triggerNode.set({triggers: new Backbone.Collection()}, {silent: true})

                    }
                    cur.set('exists', $('#existsField').val());

                    //replace this, hardcoded for enc_dx, to create a new collection named after the currently loaded
                    //template, in the case that such a collection doesnt already exist in triggers
                    if (!panel.triggerNode.get('triggers').get('enc_dx')){
                        panel.triggerNode.get('triggers').set('enc_dx', new Backbone.Collection())
                    }
                    //replace this, hard coded for enc_dx to add the new detail to the correct collection, based on
                    //which template we loaded
                    panel.triggerNode.get('triggers').get('enc_dx').add()


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
