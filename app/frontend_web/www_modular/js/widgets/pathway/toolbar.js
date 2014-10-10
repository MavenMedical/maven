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
    'pathway/modalViews/ruleWizard',

    'pathway/singleRows/pathRow',
    'pathway/internalViews/treeNodeActionSet',

    'text!templates/pathway/pathwayListEntry.html',
    'text!templates/pathway/toolbar.html',

], function ($, _, Backbone,  contextModel, curCollection, curTree,  NewPathway,  ruleWizard, PathRow, treeNodeActionSet, listEntry, toolbarTemplate) {

    var toolbar = Backbone.View.extend({
        template: _.template(toolbarTemplate),
         events: {
            'click #newpath-button': 'handle_newPath',
            'click #save-button': 'handle_save',
            'click #trigger-button': 'addTrigger'
        },

        initialize: function(){
            console.log("this.$el", this.$el)
            contextModel.on('change:page', function(){
                if (contextModel.get('page')!='pathEditor'){
                    this.$el.hide()
                } else {
                    this.$el.show()
                }
            }, this)
            this.$el.html(this.template())
            if (contextModel.get('page')!='pathEditor')
                 this.$el.hide()
            curCollection.on('sync',this.renderPathList, this)
            curTree.on('propagate', this.renderActions,this)

            this.renderPathList();
            this.renderActions();
        },
        addTrigger: function(){
            var newEditor = new ruleWizard({triggerNode: curTree})
                     newEditor.render()
        },
        renderActions: function(){

            var el = $('#node-action-set')
            console.log("find the action set", el)
            if (curTree.get('selectedNode')){
                    var myActions = new treeNodeActionSet({el: el})
                    $('#action-set', el).append(myActions.render().$el)
           }


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
