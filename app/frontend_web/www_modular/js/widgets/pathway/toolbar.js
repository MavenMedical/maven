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
    'pathway/modalViews/ruleWizard',
    'pathway/singleRows/pathRow',
    'pathway/internalViews/treeNodeActionSet',

    'text!templates/pathway/pathwayListEntry.html',
    'text!templates/pathway/toolbar.html'

], function ($, _, Backbone, contextModel, curCollection, curTree, treeContext, NewPathway, ruleWizard, PathRow, treeNodeActionSet, listEntry, toolbarTemplate) {
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
	        'change .btn-file :file': 'importPath',
            'click #exportpath-button': 'exportPath',
            'click #copypath-button': 'handle_copyPath',
            'click #testButton': 'handleTest'
        },
        handleTest: function () {
            curTree.changeNodePosition(treeContext.get('selectedNode'), -1)
        },
        initialize: function () {
            contextModel.on('change:page', function () {
                if (contextModel.get('page') != 'pathEditor') {
                    this.$el.hide()
                } else {
                    this.$el.show()
                }
            }, this)
            this.$el.html(this.template())
            if (contextModel.get('page') != 'pathEditor')
                this.$el.hide()
            //curCollection.on('sync', this.renderPathList, this)
            treeContext.on('propagate', this.renderActions, this)

            //this.renderPathList();
            this.renderActions();
        },
        addTrigger: function () {
            Backbone.history.navigate("triggereditor/" + contextModel.get('pathid') + "/node/"+contextModel.get('code'), {trigger: true});
        //    var newEditor = new ruleWizard({triggerNode: curTree})
        //    newEditor.render()
        },
        renderActions: function () {
            if (contextModel.get('page') != 'pathEditor')
                this.$el.hide()
            else {
                var el = $('#node-action-set')
                //console.log("find the action set", el)
                if (treeContext.get('selectedNode')) {
                    var myActions = new treeNodeActionSet({el: el})
                    $('#action-set', el).append(myActions.render().$el)
                }
            }


        },
        renderPathList: function () {
            $('#avail-paths').html("")
            _.each(curCollection.models, function (cur) {
                var thisRow = new PathRow({model: cur})
                $('#avail-paths').append(thisRow.render().$el)
            }, this)
        },
        handle_newPath: function () {
            a = new NewPathway({el: '#modal-target'});

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
        importPath: function () {
	    var input = $('.btn-file :file')
            file = input.get(0).files[0];
            if (file) {
                var reader = new FileReader();
                reader.readAsText(file, "UTF-8");
                reader.onload = function (evt) {
                    try{
                        var importedPath = JSON.parse(evt.target.result);
                        curTree.loadNewPathway(importedPath, {toImport: true})
                    }
                    catch(e){
                        alert("The format of the file doesn't match Pathway format. Please try another file");
                    }
		    
                }
                reader.onerror = function (evt) {
                    alert('error reading file')
                }
		input.wrap('<form>').closest('form').get(0).reset();
		input.unwrap();
            }
	},
        exportPath: function () {
           exportPathway(JSON.stringify(curTree.toJSON({'toExport':true})) , curTree.get('name')+'.pathway', 'text/plain');
        }

    });
    return toolbar;
});
