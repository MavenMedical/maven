/**
 * Created by devel on 11/16/14.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',   // lib/backbone/backbone
    'globalmodels/contextModel'
], function ($, _, Backbone, contextModel) {
    var sidebarList = [
        {'Dashboard': ['fa-tachometer', 'home']},
        {'Pathway Mgmt': ['fa-cloud', 'pathway', [
            {'Pathway Viewer': ['icon', 'pathway']},
            {'Pathway Editor': ['icon', 'pathwayEditor']}]]},
        {'Users': ['fa-user', 'users']},
        {'Reports': ['fa-bar-chart-o', 'reports']},
        {'Research': ['fa-institution', 'research']},
        {'EHR Setup': ['fa-database', 'research']}
    ];

    var Sidebar = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template);
            this.render();
        },
        events:{
          'click a': 'setPage'
        },
        setPage: function(e){
            e.preventDefault();
            var href = $(e.currentTarget).attr("href");
            contextModel.set({page:href})
        },
        appendOption : function (opt, list) {
        var elem = function(page , icon , menu_text) {
            return $('<li>', {'class': ""}).append(
                $('<a>', {
                    'href': page,
                    'class': "dropdown-toggle"}).append(
                    $('<i>', {
                        'class': 'menu-icon fa '+ icon}))
                    .append(
                    $('<span>', {
                        'class': 'menue-text',
                        'text': menu_text})
                )
                    .append(
                    $('<b>', {'class': "arrow"})
                )
            )
        };

        list = typeof list !== 'undefined' ? list : '#sidebar-list';
        for (o in opt) {
            var option = elem(opt[o][1], opt[o][0], o);
            if (opt[o].length == 3) {
                $(option.children()[0]).append($('<b>',{'class':"arrow fa fa-angle-down"}))
                 var suboption = $('<ul>', {'class':"submenu"});
                var submenu = opt[o][2];
                for (s in submenu) {
                    this.appendOption(submenu[s], suboption);
                }
            option.append(suboption);
            }
            option.appendTo(list);
        }

    },
        render: function () {
            this.$el.html(this.template());
            for (o in sidebarList){
                this.appendOption(sidebarList[o]);
            }

        }

    });
    return Sidebar;
});