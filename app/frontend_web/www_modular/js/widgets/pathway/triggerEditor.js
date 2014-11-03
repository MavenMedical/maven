define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'globalmodels/contextModel',
    'globalmodels/layoutModel',
    'pathway/modalViews/detailEditor',
    'pathway/internalViews/detailGroup',
    'pathway/models/treeModel',
    'Helpers',
    'text!templates/pathway/detailSection.html'

], function ($, _, Backbone, contextModel, layoutModel, detailEditor, DetailGroup, curTree, helpers, detailSection) {

    var ruleWizard = Backbone.View.extend({
         el: '#modal-target',

        initialize: function(params){
            this.template = _.template(params.template)
                            var that = this
            curTree.get('triggers').on('add', this.render, this)

            contextModel.on('change:page', function(){
                    if (contextModel.get('page')== 'triggerEditor'){
                        this.$el.show()
                        layoutModel.set('fluidContent', false)

                    }    else {
                        this.$el.hide()
                    }
            }, this)
            if (contextModel.get('page')== 'triggerEditor'){
                 this.$el.show()
                 layoutModel.set('fluidContent', false)

            }  else {
                 this.$el.hide()
            }
            this.render()


        },
        render: function(){
            var that = this
            this.$el.html(this.template())

            $('.createButton').on('click', function(button){
                var detailType = button.currentTarget.id

                    require(['text!templates/pathway/details/' + detailType +"_editor.html"], function(template){
                        var curEditor = new detailEditor({template: _.template(template), model: new Backbone.Model(), newDetail: true, el:$('#modal-target'), triggerNode: that.triggerNode, type: detailType})
                        curEditor.render()
                    })

            })
                for (var key in curTree.get("triggers").attributes){
                        var context = this;
                        //load this detail type's template
                        require (['text!/templates/pathway/details/' + key + 'Detail.html'], function(key) {return  function(curTemplate){
                            //load the list of details of this type
                            var toList = curTree.get('triggers').get(key);
                            var toTemplate = _.template(curTemplate);
                            var sectionTemplate = _.template(detailSection);

                                        $('.detail-sections', context.$el).append(sectionTemplate({heading:helpers.detailHeadings[key]}));

                                        //create a new detail group for this detail type, and send it the collection of details of this type
                                        var cur  = new DetailGroup({el: $('.items', context.$el).last(), lineTemplate:toTemplate, list: toList, type: key})
                                        cur.render();


                        };}(key));
                   }
        }


    });
    return ruleWizard
});