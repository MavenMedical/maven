define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'nestable'

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
            			jQuery(function($){

				    $('.dd').nestable();

				$('.dd-handle a').on('mousedown', function(e){
					e.stopPropagation();
				});

				$('[data-rel="tooltip"]').tooltip();

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
