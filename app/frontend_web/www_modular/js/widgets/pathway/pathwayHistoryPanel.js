/**
 * Created by Carlos Brenneisen on 11/17/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',

    'pathway/models/pathwayCollection',
    'pathway/models/treeModel',

    'text!templates/pathway/pathwayHistoryPanel.html',

    'widgets/pathway/TreeView',
        'text!templates/pathway/treeTemplate.html',


], function ($, _, Backbone, contextModel, curCollection, curTree, pathwayHistoryPanelTemplate, TreeView, TreeTemplate) {

    var PathwayHistoryPanel = Backbone.View.extend({
        template: _.template(pathwayHistoryPanelTemplate),
        events: {
            'click #showPathwayHistory': 'handle_showHistory',
        },
        initialize: function () {
            contextModel.on('change:page', function () {
                if (contextModel.get('page') != 'pathEditor') {
                    this.$el.hide()
                } else {
                    this.$el.show()
                }
            }, this)
            this.render();
            if (contextModel.get('page') != 'pathEditor')
                this.$el.hide()
        },
	    render: function() {
            this.$el.html(this.template());
        },
        handle_showHistory: function (){
            Backbone.history.navigate("pathwayhistory/" + contextModel.get('pathid') +"/node/" + contextModel.get('code') , true);
            $('#floating-left').append("<div class='row content-row'></div>")
	        el = $('.row', $('#floating-left')).last();
            new TreeView({template: TreeTemplate, el: el})
        }
    });

    return PathwayHistoryPanel;
});