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
    'text!templates/pathway/detailSection.html',
    'text!templates/pathway/disjoinedGroups.html'

], function ($, _, Backbone, contextModel, layoutModel, detailEditor, DetailGroup, curTree, helpers, detailSection, disjoinedGroupTemplate) {
    var printGroup = function(key, curGroup, location){
        require (['text!/templates/pathway/details/' + key + 'Detail.html'], function(key) {return  function(curTemplate){
                                //load the list of details of this type
                                var toList = curGroup.get('details').get(key);
                                var toTemplate = _.template(curTemplate);
                                var sectionTemplate = _.template(detailSection);

                                            location.append(sectionTemplate({heading:helpers.detailHeadings[key]}));

                                            //create a new detail group for this detail type, and send it the collection of details of this type
                                            var cur  = new DetailGroup({group: curGroup, el: $('.items').last(), lineTemplate:toTemplate, list: toList, type: key})
                                            cur.render();


                            };}(key));

    }
    var ruleWizard = Backbone.View.extend({

         el: '#modal-target',

        initialize: function(params){
            console.log('test2', detailEditor)
            this.template = _.template(params.template)
                            var that = this
            curTree.get('triggers').on('triggerChange', this.render, this)

            contextModel.on('change:page', function(){
                    if (contextModel.get('page')== 'triggerEditor'){
                        this.$el.show()
                        this.render()
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
                        var curEditor = new detailEditor({group: curTree.get('triggers').models[0].get('details'), template: _.template(template), model: new Backbone.Model(), newDetail: true, el:$('#modal-target'), triggerNode: that.triggerNode, type: detailType})
                        curEditor.render()
                    })

            })
            $('#add-group-button').on('click', function(){
                var newGroup = new Backbone.Model();

                newGroup.set('details', new Backbone.Model())
                newGroup.set('relationship', "or")

                curTree.get('triggers').add(newGroup)
                that.render()


            })
                       var disjGroup  = _.template(disjoinedGroupTemplate)

                    for (var i in curTree.get("triggers").models){
                        var curGroup = curTree.get('triggers').models[i]

                        $('#disjoinedGroups').append(disjGroup(curGroup.attributes))
                        var context = this;
                        //load this detail type's template
                         for (var key in curGroup.get('details').attributes){
                            var copy = $('.detail-sections').last()
                            printGroup(key, curGroup, copy)
                         }
                   }
        }


    });
    return ruleWizard
});