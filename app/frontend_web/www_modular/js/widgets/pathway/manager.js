/**
 * Created by Carlos Brenneisen on 11/3/14
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/pathwayCollection',

    'pathway/singleRows/pathRow',

    'text!templates/pathway/pathwayListEntry.html',
    'text!templates/pathway/manager.html'

], function ($, _, Backbone, contextModel, curCollection, PathRow, listEntry, managerTemplate) {

    var manager = Backbone.View.extend({
        template: _.template(managerTemplate),
        initialize: function () {
            curCollection.on('sync', this.render, this)

            $("#avail-paths-list").sortable({
                connectWith: ".connectedSortableMain",
                placeholder: "ui-sortable-placeholder",
                axis: 'y',
                tolerance: "touch",
                sort: function (event, ui) {
                    //var that = $(this),
                    var that = $(this);//ui.placeholder.parent()
                    var w = ui.helper.outerHeight();
                    that.children().each(function () {
                        if ($(this).hasClass('ui-sortable-helper') || $(this).hasClass('ui-sortable-placeholder'))
                            return true;
                        // If overlap is more than half of the dragged item
                        var dist = Math.abs(ui.position.top - $(this).position().top),
                            before = ui.position.top > $(this).position().top;
                        if ((w - dist) > (w / 2) && (dist < w)) {
                            if (before)
                                $('.ui-sortable-placeholder', that).insertBefore($(this));
                            else
                                $('.ui-sortable-placeholder', that).insertAfter($(this));
                            return false;
                        }
                    });
                }
            });
        },
        render: function(){
            this.$el.html(this.template(this));
            $('#avail-paths-list').html("");
            $('#avail-paths-list').show();
            _.each(curCollection.models, function (cur) {
                var thisModel = new Backbone.Model({id: cur.get('pathid'), name: cur.get('name')})
                var thisRow = new PathRow({model: thisModel})
                $('#avail-paths-list').append(thisRow.render().$el)
            }, this)
        }
    });
return manager;
    });
