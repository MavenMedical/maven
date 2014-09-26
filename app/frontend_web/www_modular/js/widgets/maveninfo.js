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
                if (contextModel.get('page') != 'pathEditor') {
                    this.$el.show();
                } else {
                    this.$el.hide();
                }
            },
            events: {
                'click button.close':'hidePopup'

            },
            render: function () {
                var that = this;
                console.log('selectedNode', curTree.get('selectedNode').attributes)


                this.$el.html(this.template(curTree.get('selectedNode')));

                if (contextModel.get('page') != 'pathEditor') {
                this.$el.show(1000, function () {
                    /*setTimeout(function () {
                        that.$el.hide(3000);
                    }, 5000);
                    */
                });
                }


                return this;
            },
            hidePopup: function(){
                this.$el.hide(400);
            }
        })
        ;
    return MavenInfo;
})
;
