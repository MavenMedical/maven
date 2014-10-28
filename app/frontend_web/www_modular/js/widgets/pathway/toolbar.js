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
    'text!templates/pathway/toolbar.html'

], function ($, _, Backbone, contextModel, curCollection, curTree, NewPathway, ruleWizard, PathRow, treeNodeActionSet, listEntry, toolbarTemplate) {
    var exportPathway = function (strData, strFileName, strMimeType) {
                var D = document,
                    A = arguments,
                    a = D.createElement("a"),
                    d = A[0],
                    n = A[1],
                    t = A[2] || "text/plain";

                //build download link:
                a.href = "data:" + strMimeType + "charset=utf-8," + escape(strData);


                if (window.MSBlobBuilder) { // IE10
                    var bb = new Blob([strData]);
                    return navigator.msSaveBlob(bb, strFileName);
                }
                /* end if(window.MSBlobBuilder) */


                if ('download' in a) { //FF20, CH19
                    a.setAttribute("download", n);
                    a.innerHTML = "downloading...";
                    D.body.appendChild(a);
                    setTimeout(function () {
                        var e = D.createEvent("MouseEvents");
                        e.initMouseEvent("click", true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                        a.dispatchEvent(e);
                        D.body.removeChild(a);
                    }, 66);
                    return true;
                }
                ;
                /* end if('download' in a) */


                //do iframe dataURL download: (older W3)
                var f = D.createElement("iframe");
                D.body.appendChild(f);
                f.src = "data:" + (A[2] ? A[2] : "application/octet-stream") + (window.btoa ? ";base64" : "") + "," + (window.btoa ? window.btoa : escape)(strData);
                setTimeout(function () {
                    D.body.removeChild(f);
                }, 333);
                return true;
            };
    var toolbar = Backbone.View.extend({
        template: _.template(toolbarTemplate),
        events: {
            'click #newpath-button': 'handle_newPath',
            'click #save-button': 'handle_save',
            'click #trigger-button': 'addTrigger',
            'click #importpath-button': 'importPath',
            'click #exportpath-button': 'exportPath',
            'click #testButton': 'handleTest'
        },
        handleTest: function () {
            curTree.changeNodePosition(curTree.get('selectedNode'), -1)
        },
        initialize: function () {
            console.log("this.$el", this.$el)
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
            curCollection.on('sync', this.renderPathList, this)
            curTree.on('propagate', this.renderActions, this)

            this.renderPathList();
            this.renderActions();
        },
        addTrigger: function () {
            var newEditor = new ruleWizard({triggerNode: curTree})
            newEditor.render()
        },
        renderActions: function () {
            if (contextModel.get('page') != 'pathEditor')
                this.$el.hide()
            else {
                var el = $('#node-action-set')
                console.log("find the action set", el)
                if (curTree.get('selectedNode')) {
                    var myActions = new treeNodeActionSet({el: el})
                    $('#action-set', el).append(myActions.render().$el)
                }
            }


        },
        renderPathList: function () {
            $('#avail-paths').html("")
            _.each(curCollection.models, function (cur) {
                var thisModel = new Backbone.Model({id: cur.get('pathid'), name: cur.get('name')})
                var thisRow = new PathRow({model: thisModel})
                $('#avail-paths').append(thisRow.render().$el)
            }, this)
        },
        handle_newPath: function () {


            a = new NewPathway({el: '#modal-target'});

        },
        handle_save: function () {
            curTree.save()
        },
        importPath: function () {
            console.log('import pathway');
            $('.btn-file :file').on('change', function () {
                var input = $(this),
                    file = input.get(0).files[0];

                if (file) {
                    var reader = new FileReader();
                    reader.readAsText(file, "UTF-8");
                    reader.onload = function (evt) {
                        try{
                            var importedPath = JSON.parse(evt.target.result);
                            console.log("filecontent", JSON.parse(evt.target.result));
                            curTree.parse(importedPath);
                        }
                        catch(e){
                            alert("The format of the file doesn't match Pathway format. Please try another file");
                        }

                    }
                    reader.onerror = function (evt) {
                        alert('error reading file')
                    }
                }
            });
        },
        exportPath: function () {
           exportPathway(JSON.stringify(curTree.toJSON()) , curTree.get('name')+'.pathway', 'text/plain');
        }

    });
    return toolbar;
});
