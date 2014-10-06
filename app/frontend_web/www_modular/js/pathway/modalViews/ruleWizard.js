define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/modalViews/detailEditor',
    'pathway/internalViews/detailGroup',
    'pathway/models/treeModel',
    'Helpers',
    'text!templates/pathway/RuleWizard.html',
    'text!templates/pathway/detailSection.html'

], function ($, _, Backbone, detailEditor, DetailGroup, curTree, helpers, wizardTemplate, detailSection) {

    var ruleWizard = Backbone.View.extend({
         el: '#modal-target',

        initialize: function(params){
            this.triggerNode = params.triggerNode
            this.template = _.template(wizardTemplate)
            this.$el.html(this.template())
                            var that = this

            $('.createButton').on('click', function(button){
                var detailType = button.currentTarget.id
                $("#detail-modal").modal('hide');
                $('#detail-modal').on('hidden.bs.modal', function () {

                    require(['text!templates/pathway/details/' + detailType +"_editor.html"], function(template){
                        var curEditor = new detailEditor({template: _.template(template), model: new Backbone.Model(), newDetail: true, el:$('#modal-target'), triggerNode: that.triggerNode, type: detailType})
                        curEditor.render()
                    })

                })

            })


            for (var key in curTree.get("triggers").attributes){
                   //only proceed if the key is NOT in the set of attributes that arent details
                       //show the details, there are some
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
            $("#detail-modal").modal({'show':'true'});
        }


    });
    return ruleWizard
});