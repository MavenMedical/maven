/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/pathwayCollection',
    'models/treeModel',
    'modalViews/newPathway',



    'singleRows/pathRow',
     'text!templates/pathwaysList.html',

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
            var thisModel = new Backbone.Model({id: cur[0], name: cur[1]})
            var thisRow = new PathRow({model: cur})
            appendEl.append(thisRow.render().$el)
        }, this)
    },

        handle_newPath: function () {
            new NewPathway({el: '#createNewPath-modal'});

            $("#createNewPath-modal").modal({'show': 'true'});

        },
        handle_save: function(){
            curTree.save()
        }
    });
    return PathwaysList;
});
