/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file handle a hierarchy of orders view
 *              so we can handle events easier.
 * LAST MODIFIED FOR JIRA ISSUE: MAV-97
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Template
    'text!templates/orderRow.html',

    'globalmodels/contextModel',
    'singleRow/alertRow',

], function ($, _, Backbone, orderRowTemplate, contextModel, AlertRow) {

    var OrderRow = Backbone.View.extend({
        tagName: 'div',
        template: _.template(orderRowTemplate),
        render: function(){
            $(this.el).html(this.template($.extend({viewid:this.cid},this.model.toJSON())));
            return this;
        },
        events : function() {
          //Load alerts related to this order whenever the detail portion is expanded
            var that = this;
            $(document).ready(function() {
                $(that.el).unbind('click');
                $(that.el).on('click', function (e) {


                    //only grab alert data if request has not already been made
                    if ($(that.el).find(".orderalerts").is(':empty')) {
                        $.ajax({
                            url: "/alerts",
                            data: $.param(contextModel.toParams()) + "&order_id=" + that.model.get("id"),
                            success: function (data) {
                                for (var i = 0; i < data.length; i++) {
                                    var alertrow = new AlertRow({model: data[i]});
                                    alertrow.render = function () {
                                        $(this.el).html(this.template(this.model));
                                        return this;
                                    };
                                    //$(that.el).html(this.template(this.model.toJSON()));
                                    $(that.el).find(".orderalerts").append(alertrow.render().el);

                                    // $(that.el).find(".orderalerts").append(data[i].alerttype + ": " + data[i].html);
                                }
                            }
                        });
                    }
                });
            });
       }

    });

    return OrderRow;

});
