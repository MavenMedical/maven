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
    'pathway/models/treeContext',

    'pathway/modalViews/newPathway',
    'pathway/modalViews/editNode',
    'pathway/modalViews/nodeEditor',
    'pathway/modalViews/protocolEditor',
     'pathway/modalViews/DeleteDialog',

    'pathway/modalViews/ruleWizard',
    'pathway/singleRows/pathRow',
    'pathway/internalViews/treeNodeActionSet',

    'text!templates/pathway/pathwayListEntry.html',
    'text!templates/pathway/toolbar.html'

], function ($, _, Backbone, contextModel, curCollection, curTree, treeContext,
             NewPathway, editNode, NodeEditor, ProtocolEditor,deleteDialog,
             ruleWizard, PathRow, treeNodeActionSet, listEntry, toolbarTemplate) {


    var exportPathway = function (strData, strFileName, strMimeType) {
	require(['libs/jquery/Blob', 'libs/jquery/FileSaver.min'], function(blob, saveAs) {
	    var b = new Blob([strData], {type: strMimeType});
	    saveAs(b, strFileName);
	});
    };
    var toolbar = Backbone.View.extend({
        template: _.template(toolbarTemplate),
        events: {
            'click #newpath-button': 'handle_newPath',
            'click #trigger-button': 'addTrigger',
            'click #exportpath-button': 'exportPath',
            'click #copypath-button': 'handle_copyPath',
            'click #publishpath-button': 'handle_publishPath',
            'click #editNode-button': 'editNode',
            'click #deleteNodeButton': 'deleteNode',
            'click #addChildButton': 'addChild',
            'click #addProtocolButton': 'addProtocol',
            'click #collapseButton': 'expandCollapse',
            'click #previewButton': 'previewPathway',
            'click #testButton': 'handleTest'
        },
        handleTest: function () {
            curTree.changeNodePosition(treeContext.get('selectedNode'), -1)
        },
        initialize: function () {
            this.preview = false;
            contextModel.set({preview: false});
           if(treeContext.get('selectedNode')){
		        var selected = treeContext.get('selectedNode')
                this.$el.html(this.template({treeNode: selected.attributes, childrenHidden: selected.childrenHidden && selected.childrenHidden(), page: contextModel.get('page'), preview: contextModel.get('preview')}))
            } else {
                this.$el.html(this.template({treeNode: null, childrenHidden: null, page: contextModel.get('page'), preview: contextModel.get('preview')}))
           }
            contextModel.on('change:page', this.showhide, this)
            this.showhide();
            treeContext.on('propagate', this.renderActions, this)
            this.renderActions();

        },
        showhide: function(){
            if(contextModel.get('page') == 'pathEditor'){
                this.$el.show();
                $('#toolbar').show()
                if(! this.preview) {
                    $('#widget-toolbox').addClass('grid')
                }

            }else{
                this.$el.hide();
                 $('#toolbar').hide()
                $('#widget-toolbox').removeClass('grid')
            }
        },
        addTrigger: function () {
            //clear previous modals
           $('#modal-target').empty();
            $('#detailed-trigger-modal').empty();
            a = new ruleWizard({el: '#modal-target'});

        },
        renderActions: function () {
                if (treeContext.get('selectedNode')) {
                    var selected = treeContext.get('selectedNode')
                this.$el.html(this.template({treeNode: selected.attributes, childrenHidden: selected.childrenHidden && selected.childrenHidden(), page: contextModel.get('page'), preview: contextModel.get('preview')}))
                }



        },
        renderPathList: function () {
            $('#avail-paths').html("")
            _.each(curCollection.models, function (cur) {
                var thisRow = new PathRow({model: cur})
                $('#avail-paths').append(thisRow.render().$el)
            }, this)
        },
        handle_newPath: function (e) {
            e.preventDefault();
            a = new NewPathway({el: '#modal-target'});
        },
        handle_publishPath: function (e) {
            e.preventDefault();

            var r = confirm("Are you sure you want to push this version of the pathway into production?");
            if (r != true) return;

            $.ajax({
                type: 'POST',
                url: "/history/"  + contextModel.get("canonical") + "/" + curTree.get('pathid'),
                dataType: "json",
                success: function (data) {
                    console.log("Pathway version published");
                }
            });
        },
        handle_copyPath: function(){
            $.ajax({
                type: 'GET',
                url: "/pathway_version?" + $.param(contextModel.toParams()),
                dataType: "json",
                success: function (data) {
                    //curTree.loadNewPathway({name: data['full_spec']['name'], folder: data['folder']});
                    curCollection.addNewPath();
                }
            });
        },
        exportPath: function () {
           exportPathway(JSON.stringify(curTree.toJSON({'toExport':true})) , curTree.get('name')+'.pathway', 'text/plain');
        },
        addChild : function(){

            var newEditor = new NodeEditor(treeContext.get('selectedNode'))
        },
        addProtocol: function(){
            var newEditor = new ProtocolEditor(treeContext.get('selectedNode'))
        },
        expandCollapse: function(){
                           if (!treeContext.get('selectedNode').childrenHidden()){
                               curTree.collapse(treeContext.get('selectedNode'))
                           } else{
                               treeContext.get('selectedNode').showChildren()
                           }
            curTree.getShareCode()
            treeContext.trigger('propagate')
        },
        editNode: function(){
            new editNode();

        },

        deleteNode: function(){
            new deleteDialog()


        },
        previewPathway: function(){
            if (! this.preview) {
                $('#previewButton').addClass('active');
                contextModel.set({'preview': true});
                 treeContext.trigger('propagate');
                $('#widget-toolbox').removeClass('grid')
                this.preview = true;
            } else {
                $('#previewButton').removeClass('active');
                contextModel.set({'preview': false});
                 treeContext.trigger('propagate');
                $('#widget-toolbox').addClass('grid')
                this.preview = false;
            }
        }

    });
    return toolbar;
});
