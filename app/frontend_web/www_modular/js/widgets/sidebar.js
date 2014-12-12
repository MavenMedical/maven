/**
 * Created by devel on 11/16/14.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',   // lib/backbone/backbone
    'ace',
    'globalmodels/contextModel',
    'widgets/pageOption'
], function ($, _, Backbone, ace, contextModel, pageOption) {
    var sidebarList = [
        {'Dashboard': ['fa-tachometer', 'home']},
        {'Pathway Mgmt': ['fa-cloud', 'pathway', [
            {'Pathway Viewer': ['icon', 'pathway']},
            {'Pathway Editor': ['icon', 'pathwayEditor']}]]},
        {'Users': ['fa-user', 'users']},
        {'Reports': ['fa-bar-chart-o', 'reports']},
        {'Research': ['fa-institution', 'research']},
        {'EHR Setup': ['fa-database', 'research']},
      //  {'Customers':['fa-user', 'customers']}
    ];

    var Sidebar = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template);
            this.render();

        },
        render: function () {

            this.$el.html(this.template());

             //$('#sidebar').ace_sidebar();
            //for (o in sidebarList){
               new pageOption(sidebarList[0]);
          // }

        }

    });
    return Sidebar;
});