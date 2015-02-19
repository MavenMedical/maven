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
    'globalmodels/sidebarModel',
    'widgets/pageOption',
    'text!../templates/sidebar.html'
], function ($, _, Backbone, ace, contextModel, sidebarModel, PageOption, sidebarTemplate) {
    //This list has been deprecated. Each widget appends its option to the sidebar
    var sidebarMap = {
        'Dashboard': ['fa-tachometer', 'home'],
        'Pathway Mgmt': ['fa-cloud', 'pathway', [
            {'Pathway Viewer': ['icon', 'pathway']},
            {'Pathway Editor': ['icon', 'pathwayEditor']}]],
        'Users': ['fa-user', 'users'],
        'Reports': ['fa-bar-chart-o', 'reports'],
        'Research': ['fa-institution', 'research'],
        'EHR Setup': ['fa-database', 'research'],
        'Customers':['fa-user', 'customers']
    }

    var Sidebar = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(sidebarTemplate);
            this.render();
            sidebarModel.on('change', this.change, this)
        },
        change: function() {
            _.each(sidebarModel.changed, function(v, k) {
                var obj = {}
                obj[k]=v
                new PageOption(obj)
            })
        },
        el: '#sidebar',
        render: function () {

            this.$el.html(this.template());

             //$('#sidebar').ace_sidebar();
            //for (o in sidebarList){
          // }

        }

    });
    return Sidebar;
});
