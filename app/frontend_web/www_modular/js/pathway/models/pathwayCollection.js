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
        makeSortable: function(){
            that = this;
            $('ol.sortable-folder').nestedSortable({
                forcePlaceholderSize: true,
			    handle: 'div',
                connectWith:'li, ol',
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
                branchClass: 'mjs-nestedSortable-branch',
                leafClass: 'mjs-nestedSortable-leaf',
                isAllowed:function(item, parent){
                    if (parent==null) return true;
                    if (parent.hasClass("sub-folder") || parent.hasClass("sub-folder")) return true;
                    return false;
                },
                receive: function(event, ui){
                    //when a pathway or folder is moved, we need to update the path(s) in the database
                    var path = that.getParents(ui.item).join("/");

                    if ($(ui.item).hasClass('pathrow-sortable')){
                        //pathway was moved
                        //var canonical_id = $(".path-row", $(ui.item)).attr("id");
                        that.handleMovedFolder($(ui.item).closest('.sub-folder'), path, that, false)
                    }
                    else {
                        //entire folder was moved; need to update all contained pathways
                        that.handleMovedFolder($(ui.item).closest('.sub-folder'), path, that, true)
                    }

                }
            });
        },
        getParents: function(item) {
            //get the parents of an item (pathway or folder)

            var parentList = [];
            if ($(item).hasClass('sub-folder')) {
                parentList.push($(item).children().first().attr("name")); //initialize with current folder name if folder
            }
            var parentFolder = $(item).parent().closest(".sub-folder");
            while (parentFolder.length){
                var parentName = parentFolder.children(".pathway-folder-title").attr('name');
                parentList.push(parentName);
                parentFolder = $(parentFolder).parent().closest(".sub-folder");
            }
            parentList.reverse();
            return parentList;
        },
        handleMovedPath: function(canonical_id, locationData){
            //update order
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
        },
        handleMovedFolder: function(folder, path, that, recursive){
            var position = 0;
            $(folder).children('ol').children().each(function(){
                if ($(this).hasClass("pathrow-sortable")){
                    //update order
                    position++;
                    var locationData = { "location": path, "position": position}
                    var canonical_id = $(".path-row", $(this)).attr("id");
                    that.handleMovedPath(canonical_id, locationData)
                }
                else if (recursive){
                    new_path = path + "/" + $(".pathway-folder-title",$(this)).first().attr('name');
                    that.handleMovedFolder(this, new_path, that);
                }
            });

        }

    })
    pathCollection = new pathCollection()
    return pathCollection

});
