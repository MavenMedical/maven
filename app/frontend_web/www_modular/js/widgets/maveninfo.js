/**
 * Created by Asmaa Aljuhani on 8/8/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel',
    'pathway/models/treeContext',
], function ($, _, Backbone, contextModel, curTree, treeContext) {
    var MavenInfo = Backbone.View.extend({

            initialize: function (arg) {
                this.template = _.template(arg.template);
                treeContext.on('propagate', this.render, this);
                contextModel.on('change:page change:pathid', this.hidePopup, this);
            },
            showhide: function () {
                this.$el.show();
            },
            events: {
                'click button.close': 'hidePopup'
            },
            render: function () {
                if (!treeContext.get('selectedNode')) {
                    this.hidePopup()
                    return
                }
                if (treeContext.get('selectedNode') == this.selectedNode) {
                    return
                }

                //console.log('selectedNode', treeContext.get('selectedNode'));
                // for accounts with no pathways
                if (typeof treeContext.get('selectedNode') !== 'undefined') {

                    var that = this;
                    // Don't show if there is no text or if selected node is Protocol
                    if (treeContext.get('selectedNode').attributes.sidePanelText && !treeContext.get('selectedNode').attributes.isProtocol) {
                        this.hidePopup();
                        // this.$el.hide(); // hide previous side-popup
                        this.selectedNode = treeContext.get('selectedNode');
                        this.$el.html(this.template(treeContext.get('selectedNode').attributes));

                        this.showPopup();
                        //console.log($("#mavenInfo-header").width(), $("#mavenInfo-title").outerWidth())
                    } else {
                        this.hidePopup();
                    }
                } else {
                    this.hidePopup()
                }
                //         return this;
            },
            hidePopup: function () {
                this.$el.hide();
                this.selectedNode = treeContext.get('selectedNode');
            },
            showPopup: function () {
                $('#side-popup').css('top', 'none');
                $('#side-popup').css('left', 'none');
                $('#side-popup').css('bottom', 5);
                $('#side-popup').css('right', 11);
                this.$el.show(1000);
            }
        })
        ;
    return MavenInfo;
})
;
