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
    var printGroup = function (key, curGroup, location) {

        require(['text!/templates/pathway/details/' + key + 'Detail.html'], function (key) {
            return  function (curTemplate) {

                //load the list of details of this type
                var toList = curGroup.get('details').get(key);
                var toTemplate = _.template(curTemplate);
                var sectionTemplate = _.template(detailSection);


                //create a new detail group for this detail type, and send it the collection of details of this type
                var cur = new DetailGroup({group: curGroup, lineTemplate: toTemplate, list: toList, type: key})

                location.append(cur.render().$el);


            };
        }(key));

    };
    var ruleWizard = Backbone.View.extend({
        el: '#modal-target',

        initialize: function (params) {
            if (treeContext.get('selectedNode')){
                this.activeTriggers = treeContext.get('selectedNode').get('triggers')
                this.activeNodeID = treeContext.get('selectedNode').get('nodeID')
            } else {
                this.activeTriggers = curTree.get('triggers')
                this.activeNodeID = curTree.get('nodeID')
            }

            var that = this;
            this.template = _.template(wizardTemplate)
            this.$el.html(this.template())
            $('.detailButton').draggable({ revert: true })
            this.render();
            curTree.on('sync', function () {
                that.render()
            })
            $("#detail-modal").modal({'show': 'true'});

        },
        render: function () {
            this.activeTriggers = curTree.getNodeByID(this.activeNodeID).get('triggers')
            var parent = this;
            var self = this

            //internal group view
            var groupView = Backbone.View.extend({
                template: _.template(disjoinedGroupTemplate),
                initialize: function (param) {
                    var self = this;
                    var that = this;
                    this.group = param.group
                    this.$el.droppable({
                        drop: function (event, ui) {
                            console.log(self.group)
                            var detailType = ui.draggable[0].id


                            require(['text!templates/pathway/details/' + detailType + "_editor.html"], function (template) {
                                var curEditor = new detailEditor({group: self.group, template: _.template(template), model: new Backbone.Model(), newDetail: true, el: $('#detailed-trigger-modal'), triggerNode: that.triggerNode, type: detailType})
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


                    var params = {relationship: this.group.get('relationship'), groupID: this.group.cid}
                    this.$el.html(this.template(params))

                    $('.group-delete', self.$el).on('click', function (e) {
                        parent.activeTriggers.remove(self.group)
                        /*    var id =e.currentTarget.id;
                         var group = '#group-'+id.substr(id.indexOf('-')+1)
                         console.log(group, self.group);
                         $(group).parent().remove(); */


                    })


                    if (self.group.get('relationship') == "and") {
                        $(".toggles", this.$el).bootstrapSwitch("state", false, false)
                    } else {
                        $(".toggles", this.$el).bootstrapSwitch("state", true, false)
                    }
                    $(".relSwitch", this.$el).on('click', function (a, b) {
                        if ($(".relSwitch", self.$el)[0].checked == false) {
                            self.group.set('relationship', "or")
                        }
                        else {
                            self.group.set('relationship', "and")
                        }


                    })

                    for (var key in this.group.get('details').attributes) {
                        var location = $('.detail-sections', this.$el)
                        printGroup(key, this.group, location)
                    }
                    return this


                }
            })
            $('#add-group-button').off('click');
            $('#add-group-button').on('click', function () {
                self.activeTriggers.addGroup("and")
                var models = treeContext.get('selectedNode').get('triggers').models
                var newGroup = new groupView({group: models[models.length - 1]})
                $('#disjoinedGroups').append(newGroup.$el)
                newGroup.render();

            })

            $('#disjoinedGroups').empty();
            for (var i in this.activeTriggers.models) {
                var curGroup = new groupView({group: self.activeTriggers.models[i]})
                $('#disjoinedGroups').append(curGroup.$el)
                curGroup.render()

            }


        }


    });
    return ruleWizard
});