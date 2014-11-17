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
            this.el = params.el;



        },
        render: function () {
            this.$el.html("");
            var type = this.type;
            var panel = this

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
                    $('.detail-item', this.$el)[0].onclick = function () {

                        require(['text!/templates/pathway/details/' + type + '_editor.html'],
                            function (curTemplate) {

                                var curView = new DetailEditor({group: that.group, model: that.detail, el: $('#modal-target'), template: _.template(curTemplate), type: type});
                                curView.render()

                            }
                        );
                    }
                    //if the user clicks the '.remove-detail' X in the line remove the detail
                    $('.remove-detail', this.$el)[0].onclick = function () {
                        that.group.get('details').get(type).remove(that.detail);

                    }

                }
            })
            //for each detail in the list create a spot for a detailLine view and create a detailLine view to be rendered in that spot
            this.list.each(function (cur) {
                cur.off('change')
                //rerender the group if one of the details within it changes
                cur.on('change', this.render, this)
                //create a div in which to render the new detail line
                this.$el.append("<div class = 'item-holder'></div>")
                //create the detail line to be rendered in the div, set the text to use the line template
                new detailLine({group: this.group, el: $('.item-holder', this.$el).last(), text: this.lineTemplate(cur.attributes), detail: cur})


            }, this);

            return this;

        }

    });

    return DetailGroup;

});
