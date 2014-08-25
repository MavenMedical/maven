/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
   'globalmodels/contextModel',
    'pathway/models/treeModel',
    'pathway/internalViews/treeNodeActionSet',
    'text!templates/pathway/actionList.html'
], function ($, _, Backbone, contextModel,  curModel, treeNodeActionSet, actionListTemplate) {

    var ActionList = Backbone.View.extend({
        template: _.template(actionListTemplate),

        initialize: function () {
            contextModel.on('change:selectedNode', this.render, this)

            this.render();
        },
        render: function () {
            this.$el.html(this.template());
            if (contextModel.get('selectedNode')){
                var myActions = new treeNodeActionSet()
                    $('#action-set', this.$el).append(myActions.render().$el)
                }

         }


    });
    return ActionList;
});
