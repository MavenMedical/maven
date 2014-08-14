/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/treeModel',
    'text!templates/actionList.html'
], function ($, _, Backbone, contextModel,  curModel, actionListTemplate) {

    var ActionList = Backbone.View.extend({
        template: _.template(actionListTemplate),

        initialize: function () {
            contextModel.on('change:selectedNode', this.loadModelActions, this)

            this.render();
        },
        render: function () {
            this.$el.html(this.template());
        },
        loadModelActions: function(){
        }


    });
    return ActionList;
});
