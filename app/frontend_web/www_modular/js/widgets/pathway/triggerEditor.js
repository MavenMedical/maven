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
    'text!templates/pathway/disjoinedGroups.html',
    'bootstrapswitch'


], function ($, _, Backbone, contextModel, layoutModel, detailEditor, DetailGroup, curTree, helpers, detailSection, disjoinedGroupTemplate) {
    var printGroup = function (key, curGroup, location) {
        require(['text!/templates/pathway/details/' + key + 'Detail.html'], function (key) {
            return  function (curTemplate) {
                //load the list of details of this type
                var toList = curGroup.get('details').get(key);
                var toTemplate = _.template(curTemplate);
                var sectionTemplate = _.template(detailSection);

                location.append(sectionTemplate());

                //create a new detail group for this detail type, and send it the collection of details of this type
                var cur = new DetailGroup({group: curGroup, el: $('.items').last(), lineTemplate: toTemplate, list: toList, type: key})

                cur.render();


            };
        }(key));

    }
    var ruleWizard = Backbone.View.extend({

        el: '#modal-target',

        initialize: function (params) {
            this.template = _.template(params.template)
            var that = this

            contextModel.on('change:page', function () {
                if (contextModel.get('page') == 'triggerEditor') {
                    this.$el.show()
                    this.render()
                    layoutModel.set('fluidContent', false)
                } else {
                    this.$el.hide()
                }
            }, this)
            if (contextModel.get('page') == 'triggerEditor') {
                this.$el.show()
                layoutModel.set('fluidContent', false)

            } else {
                this.$el.hide()
            }
            this.render()


        },
        render: function () {
            var that = this
            curTree.once('sync', function () {
                that.render()
            })

            this.$el.html(this.template())
            $('#back-to-editor').on('click', function () {
                Backbone.history.navigate("pathwayeditor/" + contextModel.get('pathid') + "/node/" + contextModel.get('code'), {trigger: true});
            })

            $('.createButton').draggable({ revert: true })
            $('#add-group-button').on('click', function () {

                curTree.get('selectedNode').get('triggers').addGroup("and")


            })
            var groupView = Backbone.View.extend({
                template: _.template(disjoinedGroupTemplate),
                initialize: function (param) {
                    this.group = param.group

                },
                render: function () {
                    var self = this;
                    this.$el.css({'border-style': 'solid', 'border-width': '4px'})
                    this.$el.droppable({
                        drop: function (event, ui) {
                            var detailType = ui.draggable[0].id

                            require(['text!templates/pathway/details/' + detailType + "_editor.html"], function (template) {

                                var curEditor = new detailEditor({group: self.group, template: _.template(template), model: new Backbone.Model(), newDetail: true, el: $('#detailed-trigger-modal'), triggerNode: that.triggerNode, type: detailType})

                                curEditor.render()
                            })


                        },
                        activeClass: "activeDrop",
                        hoverClass: "hoverDrop"
                    })


                    var params = {relationship: this.group.get('relationship'), groupID: this.group.cid}
                    this.$el.html(this.template(params))

                    $('.group-delete', this.$el).on('click', function () {
                        curTree.get('selectedNode').get('triggers').remove(self.group)
                    })

                    $(".toggles", this.$el).bootstrapSwitch()
                    $(".toggles", this.$el).bootstrapSwitch('onText', "Any")
                    $(".toggles", this.$el).bootstrapSwitch('offText', "All")

                    if (self.group.get('relationship') == "and") {
                        $(".toggles", this.$el).bootstrapSwitch("state", false, false)
                    } else {
                        $(".toggles", this.$el).bootstrapSwitch("state", true, false)
                    }
                    $(".toggles", this.$el).on('switchChange.bootstrapSwitch', function (a, b) {
                        if ($(".toggles", self.$el).bootstrapSwitch('state') == false) {
                            self.group.set('relationship', "and")
                        }
                        else {
                            self.group.set('relationship', "or")
                        }


                    })

                    for (var key in this.group.get('details').attributes) {
                        var location = $('.detail-sections', this.$el)
                        printGroup(key, this.group, location)
                    }
                    return this


                }
            })

            for (var i in curTree.get("triggers").models) {
                var curGroup = new groupView({group: curTree.get('selectedNode').get('triggers').models[i]})
                $('#disjoinedGroups').append(curGroup.$el)
                $('#disjoinedGroups').append("<div style='height:25px'></div>")
                curGroup.render()


            }


        }



    });
    return ruleWizard
});