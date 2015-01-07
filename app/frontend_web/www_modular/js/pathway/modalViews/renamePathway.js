/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */


define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'pathway/models/treeModel',
    'text!templates/pathway/renamePathway.html',
    'globalmodels/contextModel',

], function ($, _, Backbone, curTree, renameTemplate, contextModel) {
    var NewPathway = Backbone.View.extend({
        template: _.template(renameTemplate),
        canonical_id: 0,
        nameEl: null,
        events: {
            'click #rename-button': 'handle_Rename',
            'keyup #newName': 'keyup_Rename',
        },
        initialize: function (params) {

            if (typeof params.canonical_id !== 'undefined'){
                this.canonical_id = params.canonical_id;
            }
            if (typeof params.nameEl !== "undefined") {
                this.nameEl = params.nameEl;
            }

            this.$el.html(this.template());

            $("#renamepathwaymodal").modal({'show':'true'});
        },
        keyup_Rename: function(event){
            if (event.keyCode==13) this.handle_Rename();
            else return;
        },
        handle_Rename: function(){
            //hide modal
            var newName = $('#newName').val();
            $(this.nameEl).html(newName);
            //curTree.loadNewPathway({name: $('#newName').val(), folder: this.parentList, parentFolder: this.parentFolder});
            var url = "/protocol/" + this.canonical_id + "/" + contextModel.get("customer_id");
            var extraData = {'new_name': newName};
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: url,
                data: JSON.stringify(extraData),
                error: function (){
                    alert("Could not rename pathway");
                }
           });

           $("#renamepathwaymodal").modal('hide');


            this.undelegateEvents(); // Unbind all local event bindings

            delete this.$el; // Delete the jQuery wrapped object variable
            delete this.el; // Delete the variable reference to this node
        }
    });
    return NewPathway;

});