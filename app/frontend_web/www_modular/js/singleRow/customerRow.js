/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Carlos Brenneisen'
 * DESCRIPTION: This Javascript file is for handling customer row events
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'text!templates/customerRow.html',

    'widgets/widgetModal',
    'widgets/userList',
    'widgets/adminSettings'

], function ($, _, Backbone, contextModel, customerRowTemplate, WidgetModal, userList, adminSettings) {
    var customerRow = Backbone.View.extend({
        tagName: 'tr class=\'customer-row\'',
        template: _.template(customerRowTemplate),
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        events: function() {
            var that = this;
            $(document).ready(function() {
                $(that.el).unbind('click');
                $(that.el).on('click', function (e) {
                    //hide all customer edit fields in case others are active
                    $(".customer-row > td").each(function(){
                        $(this).find(".customer-row-val").html($(this).find(".customer-row-edit").val());
                    });
                    $(".customer-row-edit").hide();
                    $(".customer-row-val").show();

                    if (!$(".customer-info-click", this.$el).is(e.target) &&
                        $(".customer-info-click", this.$el).has(e.target).length === 0) {

                        //show customer edit fields for this row if target is not the info click button
                        $(that.el).find(".customer-row-val").hide();
                        $(that.el).find(".customer-row-edit").each(function () {
                            $(this).width($(this).parent().width() - 5);
                            //  $(this).attr('width')
                            $(this).show();
                        });
                    }
                    else
                    {
                        //show customer info modal if user clicked on 'view info' button
                        var widgetModal = new WidgetModal({widgetList: [adminSettings, userList]});
                        widgetModal.render({target_customer: that.model.attributes.customer_id});
                    }
                });
            });
        }
    });

    return customerRow;

});
