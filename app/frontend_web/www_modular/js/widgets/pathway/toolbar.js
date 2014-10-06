/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/pathwayCollection',
    'pathway/models/treeModel',
    'pathway/modalViews/newPathway',
    'pathway/singleRows/pathRow',

    'text!templates/pathway/pathwayListEntry.html',
    'text!templates/pathway/toolbar.html',

], function ($, _, Backbone,  contextModel, curCollection, curTree,  NewPathway,  PathRow, listEntry, toolbarTemplate) {

    var toolbar = Backbone.View.extend({
        template: _.template(toolbarTemplate),
         events: {
            'click #newpath-button': 'handle_newPath',
            'click #save-button': 'handle_save'
        },

        initialize: function(){
            contextModel.on('change:page', function(){
                if (contextModel.get('page')!='pathEditors'){
                    this.$el.hide()
                } else {
                    this.$el.show()
                }
            }, this)
            this.$el.html(this.template())
            if (contextModel.get('page')!='pathEditor')
                 this.$el.hide()
            curCollection.on('sync',this.renderPathList, this)
            this.renderPathList();
        },
        renderPathList: function(){
             $('#avail-paths').html("")
            _.each(curCollection.models, function(cur){
             var thisModel = new Backbone.Model({id: cur.get('pathid'), name: cur.get('name')})
             var thisRow = new PathRow({model: thisModel})
             $('#avail-paths').append(thisRow.render().$el)
        }, this)
        },
         handle_newPath: function () {
            a = new NewPathway({el: '#modal-target'});

        },
        handle_save: function(){
            curTree.save()
        }
    });
    return toolbar;
});
