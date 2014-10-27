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
], function ($, _, Backbone, contextModel,  curTree, treeNodeActionSet, actionListTemplate) {

    var ActionList = Backbone.View.extend({
        template: _.template(actionListTemplate),

        initialize: function () {
            var that = this
             curTree.on('all', function(){
                    that.render()
                })
	    contextModel.on('change:page', this.showhide, this);

            if (contextModel.get('page') != 'pathEditor')
               return;
            this.render();
        },
	showhide: function() {
	    if (contextModel.get('page') == 'pathEditor') {
		this.$el.show(); 
	    } else {
		this.$el.hide();
	    }
	},		    
        render: function () {
	    this.showhide();
            this.$el.html(this.template());
            if (curTree.get('selectedNode')){
                var myActions = new treeNodeActionSet()
                    $('#action-set', this.$el).append(myActions.render().$el)
                }

         }


    });
    return ActionList;
});
