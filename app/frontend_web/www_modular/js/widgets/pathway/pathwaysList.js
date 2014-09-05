/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/models/pathwayCollection',
    'pathway/models/treeModel',
    'pathway/modalViews/newPathway',



    'pathway/singleRows/pathRow',
     'text!templates/pathway/pathwaysList.html',

], function ($, _, Backbone,  curCollection, curTree,  NewPathway, PathRow, pathwaysListTemplate) {

    var PathwaysList = Backbone.View.extend({
        template: _.template(pathwaysListTemplate),
         events: {
            'click #newpath-button': 'handle_newPath',
            'click #save-button': 'handle_save'
        },
	initialize: function(){
	    curCollection.on('sync',this.render, this)
        this.render();

	},
	render: function(){
        this.$el.html(this.template());
        var appendEl =  $('.table-body', this.$el)
        _.each(curCollection.models, function(cur){
            var thisModel = new Backbone.Model({id: cur.get('pathid'), name: cur.get('name')})
            var thisRow = new PathRow({model: thisModel})
            appendEl.append(thisRow.render().$el)
        }, this)
    },

        handle_newPath: function () {
            a = new NewPathway({el: '#modal-target'});

        },
        handle_save: function(){
            curTree.save()
        }
    });
    return PathwaysList;
});
