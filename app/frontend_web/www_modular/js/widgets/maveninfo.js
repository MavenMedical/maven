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
                if (!curTree.get('selectedNode')){
                    return
                }
                // for accounts with no pathways
                if(typeof curTree.get('selectedNode') !== 'undefined') {

                    var that = this;
                    // Don't show if there is no text or if selected node is Protocol
                    if (!(curTree.get('selectedNode').attributes.sidePanelText == "" || curTree.get('selectedNode').attributes.isProtocol )
                        && !(this.selectedNode == curTree.get('selectedNode'))) {
                        this.$el.hide(); // hide previous side-popup
                        this.selectedNode = curTree.get('selectedNode');
                        this.$el.html(this.template(curTree.get('selectedNode').attributes));
                        $('#side-popup').css('top', curTree.get('selectedNodeOffset').top );
                        $('#side-popup').css('left',  curTree.get('selectedNodeOffset').left + curTree.get('selectedNodeWidth') + 10);
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
