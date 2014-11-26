define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
        'nestedSortable'

], function($, _, Backbone, contextModel){


    var pathCollection = Backbone.Collection.extend({
        elPairs: [],
        folders: {'Folder A':{'Folder B':{}, 'Folder C': {}}},
	    model: Backbone.Model.extend({idAttribute: 'canonical'}),
        url: function() {
            return '/list'
        },
        initialize: function(){
            this.fetch()

        },
        addFolder: function(folderName, parents){
            currentFolder = this.folders;
            for(var i = 0; i < parents.length; i++){
                    currentFolder = currentFolder[parents[i]];
            }
            currentFolder[folderName] = {};

        },
        saveOrder: function(){
            this.handleFolder("#avail-paths-list","", this);
        },
        makeSortable: function(){
            $('ol.sortable-folder').nestedSortable({
                forcePlaceholderSize: true,
			    handle: 'div',
			    helper:	'clone',
			    items: 'li',
			    opacity: .6,
			    placeholder: 'placeholder',
			    revert: 250,
			    tabSize: 25,
			    tolerance: 'pointer',
			    toleranceElement: '> div',
			    maxLevels: 0,
			    isTree: true,
			    expandOnHover: 700,
			    startCollapsed: true,
                doNotClear: false,
                branchClass: 'mjs-nestedSortable-branch ui-sortable',
                leafClass: 'mjs-nestedSortable-leaf ui-sortable',
                update: function(){
                    //if the folder row was moved we may need to update the path
                    that.setParents();
                },
                sort: function(){
                    //if the folder row was moved we may need to update the path
                    that.setParents();
                }
            });
        },
        handleFolder: function(folder, path, that){
            var position = 0;
            $(folder).children().each(function(){
                if ($(this).hasClass("path-row")){
                    //update order
                    position++;
                        var locationData = { "location": path,
                            "position": position,
                        }
                    var canonical_id = $(".path-header", $(this)).attr("id");
                    var data = {'canonical': canonical_id, 'customer_id': contextModel.get("customer_id"), 'userid': contextModel.get("userid")}
                    $.extend(data, contextModel.toParams(), data);
                        $.ajax({
                            type: 'POST',
                            dataType: 'json',
                            url: "/update_pathway_location?" + $.param(data),
                            data: JSON.stringify(locationData),
                            success: function () {
                                console.log("pathway location updated");
                            }
                        });
                }
                else {
                    new_path = path + "/" + $(".folder-title",$(this)).first().text();
                    that.handleFolder(this, new_path, that);
                }
            });

        }

    })
    pathCollection = new pathCollection()
    return pathCollection

});
