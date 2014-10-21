/**
 * Created by Asmaa Aljuhani on 8/8/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel'
], function ($, _, Backbone, contextModel, curTree) {
    var MavenInfo = Backbone.View.extend({

            initialize: function (arg) {
                this.template = _.template(arg.template);
                curTree.on('propagate', this.render, this);
            },
            showhide: function () {
                this.$el.show();
            },
            events: {
                'click button.close': 'hidePopup'

            },
            render: function () {
                this.$el.hide(); // hide previous side-popup
                var that = this;
                if (curTree.get('selectedNode') && curTree.get('selectedNode').attributes != null) {
                    // Don't show if there is no text
                    if (!(curTree.get('selectedNode').attributes.sidePanelText == "")) {
                        this.$el.html(this.template(curTree.get('selectedNode').attributes));

                        this.$el.show(1000, function () {
                            /* This code for auto hide
                            setTimeout(function () {
                             that.$el.hide(3000);
                             }, 5000);
                             */
                        });
                    }
                }


                //         return this;
            },
            hidePopup: function () {
                this.$el.hide(400);
            }
        })
        ;
    return MavenInfo;
})
;
