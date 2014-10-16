/**
 * Created by Carlos Brenneisen on 10/01/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',

    'text!templates/widgetModal.html',
    'widgets/userList'

], function ($, _, Backbone, contextModel, widgetModalTemplate) {

    var WidgetModal = Backbone.View.extend({
            el: $("#modal-target"),
            template: _.template(widgetModalTemplate),
            widgetList: [],
            initialize: function(arg){
                this.widgetList = arg.widgetList;
                //this.render();
            },
            events: {

            },
            render: function (data){
                //data must be a dict (can be empty)
                this.$el.html(this.template());
                $("#widget-modal").modal({'show':'true'});
                for (var i = 0; i < this.widgetList.length; i ++)
                {
                    $("#widget-modal").find('.modal-content').append("<div class='row content-row'></div>");
	                var newEl = $('#widget-modal').find('.row').last();
                    var args = {el: newEl};
                    $.extend(args, data); //add additional arguments
                    var widget = new this.widgetList[i](args);
                }
                $(document).ready(function(){
                    //stop widget buttons from closing the modal
                    $("button", this.$el).click(function(event){
                        event.stopImmediatePropagation();
                    });
                });
            },
    });

    return WidgetModal;
});
