define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbones
    'pathway/models/nodeModel',
    'globalmodels/contextModel',
    'text!templates/pathway/newPathwayFolder.html',
    'pathway/singleRows/folderRow',

], function ($, _, Backbone, NodeModel, contextModel, newPathwayFolderTemplate, FolderRow) {

    var newPathwayFolder = Backbone.View.extend({
        template: _.template(newPathwayFolderTemplate),
        el: $("#modal-target"),
        initialize: function (parent) {
            var that = this;
            this.parent = parent;
            this.$el.html(this.template(that.attributes));
            $("#detail-modal").modal({'show': 'true'});

            $("#createPathwayFolder", this.$el).on("click", function () {
                var folder_name = $("#pathwayFolderName").val();
                var thisModel = new Backbone.Model({name: folder_name});
                var thisRow = new FolderRow({model: thisModel})
                $("#pathway-directory").append(thisRow.render().$el);

                $('#detail-modal').modal('hide');
                /*
                 $.ajax({
                 type: 'POST',
                 dataType: 'json',
                 url: "/send_message?" + $.param(contextModel.toParams()) + "&target_user="+recipientUserName,
                 data: JSON.stringify({
                 "subject": "Please review this patient - " + contextModel.get("official_name"),
                 "message": message,
                 }),
                 error: function (){
                 alert("There was a problem sending the message.");
                 }
                 });
                 */


            });
        }
    });
    return newPathwayFolder;
});
