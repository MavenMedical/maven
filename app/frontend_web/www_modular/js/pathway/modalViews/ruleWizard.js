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
    'text!templates/pathway/RuleWizard.html',
    'bootstrapswitch'

], function ($, _, Backbone, contextModel, layoutModel, detailEditor, DetailGroup, curTree, helpers, detailSection, disjoinedGroupTemplate, wizardTemplate) {
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
            this.template = _.template(wizardTemplate)
            this.$el.html(this.template())
            $('.detailButton').draggable({ revert: true })
            this.render();
        },
        render: function () {

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

                            $('#detail-modal').on('hidden.bs.modal', function () {
                                require(['text!templates/pathway/details/' + detailType + "_editor.html"], function (template) {
                                    var curEditor = new detailEditor({group: self.group, template: _.template(template), model: new Backbone.Model(), newDetail: true, el: $('#detailed-trigger-modal'), triggerNode: that.triggerNode, type: detailType})
                                    curEditor.render()
                                    $("#detail-modal").modal('show');
                                })

                            })
                            $("#detail-modal").modal('hide');


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

                    $('.group-delete', this.$el).on('click', function (e) {
                        curTree.get('triggers').remove(self.group)
                        var id =e.currentTarget.id;
                        var group = '#group-'+id.substr(id.indexOf('-')+1)
                        console.log(group, self.group);
                        $(group).parent().remove();
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

             $('#add-group-button').on('click', function () {
                curTree.get('triggers').addGroup("and")
                var models = curTree.get('triggers').models
                var newGroup = new groupView({group: models[models.length -1]})
                $('#disjoinedGroups').append(newGroup.$el)
                $('#disjoinedGroups').append("<div style='height:25px'></div>")
                newGroup.render();

            })

             $('#disjoinedGroups').empty();
            for (var i in curTree.get("triggers").models) {
                var curGroup = new groupView({group: curTree.get('triggers').models[i]})
                $('#disjoinedGroups').append(curGroup.$el)
                $('#disjoinedGroups').append("<div style='height:25px'></div>")
                curGroup.render()

            }
            curTree.workaround = false;


        }


    });
    return ruleWizard
});