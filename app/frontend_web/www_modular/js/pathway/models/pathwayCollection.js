define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
     'nestedSortable'

], function($, _, Backbone, contextModel){


    var pathCollection = Backbone.Collection.extend({
	    model: Backbone.Model.extend({idAttribute: 'canonical'}),
        url: function() {
            return '/list'
        },
        initialize: function(){
            this.fetch()
        },
        addNewPath: function(){
            this.fetch({add: true})
        },
        makeSortable: function(){
            that = this;
            $('ol.dd-list').nestedSortable({
                forcePlaceholderSize: true,
			    handle: 'div:not(.bootstrap-switch)',
                connectWith:'li, ol',
			    helper:	'clone',
			    items: 'li',
			    opacity: .6,
			    placeholder: 'placeholder',
			    revert: 250,
			    tabSize: 25,
			    tolerance: 'pointer',
			    toleranceElement: '> div:not(.bootstrap-switch)',
			    maxLevels: 0,
			    isTree: true,
			    expandOnHover: 700,
			    startCollapsed: true,
                doNotClear: false,
                branchClass: 'mjs-nestedSortable-branch',
                leafClass: 'mjs-nestedSortable-leaf',
               // containment: '.dd-list',
                isAllowed:function(item, parent){
                    if (parent==null) return true;
                    if ($(parent).is("li") || $(parent).is("ol")) return true;
                    return false;
                },
                receive: function(event, ui){
                    //when a pathway or folder is moved, we need to update the path(s) in the database
                    var parents = that.getParents(ui.item);
                    var path = "";
                    if (parents.length) {
                        if (parents.length > 1) path = parents.join("/");
                        else path = parents[0];
                    }
                    var parentFolder = $(ui.item).closest('.sub-folder');
                    if (!parentFolder.length) parentFolder = $("#nestable");
/*
                    else {
                        var parentFolder = $('#avail-paths-list');
                        var path = "";
                    }*/

                    if ($(ui.item).hasClass('pathrow-item')){
                        //pathway was moved
                        //var canonical_id = $(".path-row", $(ui.item)).attr("id");
                        that.handleMovedFolder(parentFolder, path, that, false)
                    }
                    else {
                        //entire folder was moved; need to update all contained pathways
                        that.handleMovedFolder(parentFolder, path, that, true)
                    }
                },
                sort: function(event, ui){
                    if ($(ui.item).hasClass('mjs-nestedSortable-expanded')) {
                        $(ui.item).switchClass("mjs-nestedSortable-expanded", "mjs-nestedSortable-collapsed", 0);
                        $(ui.helper).switchClass("mjs-nestedSortable-expanded", "mjs-nestedSortable-collapsed", 0);
                        $(ui.placeholder).height($(ui.item).height())
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
                if (parentName == '') break;
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
                if ($(this).hasClass("pathrow-item")){
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
