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
    'pathway/models/treeContext',

    'Helpers',
    'text!templates/pathway/detailSection.html',
    'text!templates/pathway/disjoinedGroups.html',
    'text!templates/pathway/RuleWizard.html',
    'bootstrapswitch'

], function ($, _, Backbone, contextModel, layoutModel, detailEditor, DetailGroup, curTree, treeContext, helpers, detailSection, disjoinedGroupTemplate, wizardTemplate) {
    var printGroup = function (key, curGroup, location, isTrigger) {

        require(['text!/templates/pathway/details/' + key + 'Detail.html',  'pathway/internalViews/detailGroup'], function (curTemplate, DetailGroup ) {

                //load the list of details of this type
                var toList = curGroup.get('details').get(key);
                var toTemplate = _.template(curTemplate);
                var sectionTemplate = _.template(detailSection);
                //create a new detail group for this detail type, and send it the collection of details of this type
                var cur = new DetailGroup({group: curGroup, lineTemplate: toTemplate, list: toList, type: key, isTrigger: isTrigger})


                location.append(cur.render().$el);
            });


    };
    var ruleWizard = Backbone.View.extend({
        el: '#modal-target',

        initialize: function (params) {
            this.activeNodeID = treeContext.get('selectedNode').get('nodeID')

            //if the currently selected node is the tree root, load the trigger editor
            if (this.activeNodeID == curTree.get('nodeID')){
                this.type = 'triggers'
            //otherwise load the implication editor
            } else {
                this.type  = 'implications'
            }
            //load the data model triggers/implications
            this.activeTriggers = treeContext.get('selectedNode').get(this.type)
            var that = this;
            this.template = _.template(wizardTemplate)
            //load the template pass the information of whether it will be triggers or implications
            this.$el.html(this.template({isHead: this.type == 'triggers'}))
            $('.detailButton').draggable({ revert: true })
            this.render();
            //if the tree changes it will save and we will rerender this
            curTree.on('sync', function () {
                that.render()
            })
            $("#detail-modal").modal({'show': 'true'});

        },
        render: function () {
            this.activeTriggers = curTree.getNodeByID(this.activeNodeID).get(this.type)
            var parent = this;
            var self = this

            //internal group view
            //this is the view for a group of details, there may be many of these in the trigger editor but only one
            //in implications
            var groupView = Backbone.View.extend({
                template: _.template(disjoinedGroupTemplate),
                initialize: function (param) {
                    var self = this;
                    var that = this;
                    this.group = param.group
                    this.$el.droppable({
                        //when a detail type button is dropped on a group, launch a detail editor for a new detail to put in that group
                        drop: function (event, ui) {
                            console.log(self.group)
                            var detailType = ui.draggable[0].id


                            require(['text!templates/pathway/details/' + detailType + "_editor.html"], function (template) {
                                var curEditor = new detailEditor({group: self.group, template: _.template(template), model: new Backbone.Model(), newDetail: true, el: $('#detailed-trigger-modal'), triggerNode: that.triggerNode, type: detailType, isTrigger: parent.type == 'triggers'})
                                curEditor.render()

                            })


                        },
                        activeClass: "activeDrop",
                        hoverClass: "hoverDrop"
                    })

                },

                render: function () {
                    var self = this;
                    this.$el.css({'border-style': 'solid', 'border-width': '4px'})

                    //the template needs to know certain things, amalgmate them here
                    var params = {relationship: this.group.get('relationship'), groupID: this.group.cid, isHead: parent.type == 'triggers'}
                    this.$el.html(this.template(params))
                    //delete button click listener
                    $('.group-delete', self.$el).on('click', function (e) {
                        parent.activeTriggers.remove(self.group)
                        /*    var id =e.currentTarget.id;
                         var group = '#group-'+id.substr(id.indexOf('-')+1)
                         console.log(group, self.group);
                         $(group).parent().remove(); */


                    })

                    //click handler for the relationship switch invisible for implications
                    $(".relSwitch", this.$el).on('click', function (a, b) {
                        if ($(".relSwitch", self.$el)[0].checked == false) {
                            self.group.set('relationship', "or")
                        }
                        else {
                            self.group.set('relationship', "and")
                        }


                    })
                    //for each type of detail in the group, print all of their members
                    for (var key in this.group.get('details').attributes) {
                        var location = $('.detail-sections', this.$el)
                        printGroup(key, this.group, location, parent.type == 'triggers')
                    }
                    return this


                }
            })
            $('#add-group-button').off('click');
            $('#add-group-button').on('click', function () {
                self.activeTriggers.addGroup("and")
                var models = treeContext.get('selectedNode').get(self.type).models
                var newGroup = new groupView({group: models[models.length - 1]})
                $('#disjoinedGroups').append(newGroup.$el)
                newGroup.render();

            })

            $('#disjoinedGroups').empty();
            for (var i in this.activeTriggers.models) {
                //for each group in the model, make a new group view
                var curGroup = new groupView({group: self.activeTriggers.models[i]})
                //and append its el to disjoinedgroups
                $('#disjoinedGroups').append(curGroup.$el)
                curGroup.render()

            }


        }


    });
    return ruleWizard
});