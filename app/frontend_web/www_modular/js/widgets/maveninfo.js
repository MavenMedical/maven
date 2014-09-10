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
            this.$el.html(this.template());
            console.log('curTree', curTree);
            curTree.on('change:name', this.render,this);
	    contextModel.on('change:page', this.showhide, this);
	    this.showhide();
        },
	showhide: function() {
	    if (contextModel.get('page') != 'pathEditor') {
		this.$el.show(); 
	    } else {
		this.$el.hide();
	    }	    
	},
        events: {

        },
        render: function () {
            console.log('render maveninfo');
            this.$el.html(this.template(curTree.get('selectedNode').attributes))
            return this;
        }
    });
    return MavenInfo;
});
