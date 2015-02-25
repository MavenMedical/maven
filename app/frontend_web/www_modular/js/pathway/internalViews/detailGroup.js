/*


 Backbone View displaying the set of details of a particular type contained in curRule
 Displayed Under: Details
 Param:
 lineTemplate : the template to be used for single detail of the type used
 el           : the DOM element wherin to render the entire group
 list         : the set of details to render

 */


define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'pathway/models/treeModel',

    'pathway/modalViews/detailEditor',
    'text!templates/pathway/detailSection.html'
], function ($, _, Backbone, curTree, DetailEditor, detailSectionTemplate) {

    var DetailGroup = Backbone.View.extend({

        template: _.template(detailSectionTemplate),

        initialize: function (params) {
            var self = this;
            // load the params into the object
            this.lineTemplate = params.lineTemplate;
            this.list = params.list;
            this.type = params.type;
            this.group = params.group;
            this.isTrigger = params.isTrigger
            this.el = params.el;


        },
        render: function () {
            this.$el.html("");
            var type = this.type;
            var panel = this
            var that = this;
            //Backbone view representing a line to be displayed in the detail group
            //params:
            //      el: the div wherein to render the new line, used instead of append for no reason I can remember, should be refactored
            //      text: the text to be displayed in the line
            //      detail: the object model of the detail represented by the line
            var detailLine = Backbone.View.extend({

                initialize: function (params) {
                    this.el = params.el
                    this.$el.html(params.text)
                    this.group = params.group

                    this.detail = params.detail


                    var that = this
                    // if the user clicks the  el '.detail-item' link in this line, load the editor template for this detail and display the modal for editing
                    $('.detail-item', that.$el).off('click')
                    $('.detail-item', that.$el).on('click' , function () {

                        require(['text!/templates/pathway/details/' + type + '_editor.html'],
                            function (curTemplate) {

                                var curView = new DetailEditor({group: that.group, model: that.detail, el: $('#detailed-trigger-modal'), template: _.template(curTemplate), type: type});
                                curView.render()

                            }
                        );
                    })
                    //if the user clicks the '.remove-detail' X in the line remove the detail
                    $('.remove-detail', that.$el).off('click');
                    $('.remove-detail', that.$el).on('click', function () {
                        that.group.get('details').get(type).remove(that.detail);

                    })

                }
            })
            //for each detail in the list create a spot for a detailLine view and create a detailLine view to be rendered in that spot
            for (var count = 0; count < that.list.models.length; count++) {
                var cur = that.list.models[count]
                cur.off('change')
                //rerender the group if one of the details within it changes
                cur.on('change', this.render, this)
                //create a div in which to render the new detail line
                //create the detail line to be rendered in the div, set the text to use the line template
                var params = {}
                for (var i in cur.attributes) {
                    var c = cur.attributes[i]
                    if (c.models) {
                        params[i] = c.models
                    } else {
                        params[i] = c
                    }
                }
                params.isTrigger =  panel.isTrigger
                var n = new detailLine({group: that.group, text: that.lineTemplate(params), detail: cur})
                that.$el.append(n.$el)

            }
            ;

            return this;

        }

    });

    return DetailGroup;

});
