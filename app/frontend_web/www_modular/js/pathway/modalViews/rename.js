define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'pathway/models/treeModel',
    'text!templates/pathway/rename.html',
    'globalmodels/contextModel',

], function ($, _, Backbone, curTree, renameTemplate, contextModel) {
    var Rename = Backbone.View.extend({
        template: _.template(renameTemplate),
        elId: 0, //canonical or other id
        elToRename: null,
        elType: '', //folder or pathway
        events: {
            'click #rename-button': 'handle_Rename',
            'keyup #newName': 'keyup_Rename',
        },
        initialize: function (params) {

            if (typeof params.elType !== 'undefined'){
                this.elType = params.elType;
            }
            else {
                console.log("No type provided");
                return;
            }

            if (typeof params.elToRename !== "undefined") {
                this.elToRename = params.elToRename;
            }
            else {
                console.log("No element provided");
                return;
            }

            if (typeof params.elId !== 'undefined'){
                this.elId = params.elId;
            }

            this.$el.html(this.template(params));

            $("#renamemodal").modal({'show':'true'});
        },
        keyup_Rename: function(event){
            if (event.keyCode==13) this.handle_Rename();
            else return;
        },
        handle_Rename: function(){
            var newName = $('#newName').val();

            if (this.elType=='Pathway') {
                $(this.elToRename).html(newName);
                //curTree.loadNewPathway({name: $('#newName').val(), folder: this.parentList, parentFolder: this.parentFolder});
                var url = "/protocol/" + this.elId + "/" + contextModel.get("customer_id");
                var extraData = {'new_name': newName};
                $.ajax({
                    type: 'POST',
                    dataType: 'json',
                    url: url,
                    data: JSON.stringify(extraData),
                    error: function () {
                        alert("Could not rename pathway");
                    }
                });
            }
            else if (this.elType=='Folder'){
                $(this.elToRename).children(".dd2-content").children(".folder-title").html(newName);
                $(this.elToRename).children(".pathway-folder-title").attr("name", newName);

                //let the folder row handle updating the pathway location
                $(this.elToRename).trigger("change");
            }

           //hide modal
           $("#renamemodal").modal('hide');


            this.undelegateEvents(); // Unbind all local event bindings

            delete this.$el; // Delete the jQuery wrapped object variable
            delete this.el; // Delete the variable reference to this node
        }
    });
    return Rename;

});