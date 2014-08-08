/**
 * Created by Asmaa Aljuhani on 8/6/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone,
    'models/contextModel',

    'widgets/topBanner',
    'widgets/pathwaySearch',
    'widgets/pathwaysList',
    'widgets/actionList',
    'widgets/TreeView',
], function ($, _, Backbone, Context, TopBanner, PathSearch, PathwaysList, ActionList, TreeView) {

var AppRouter = Backbone.Router.extend({
    routes: {
        "" : 'showHome',
        "createpathway" : 'showNewPathway',
        //default
        '*action': 'defaultAction'
    },

    showHome: function(){
        console.log('Show page Home');
        new TopBanner({el:'#fixed-topA-1-1'});
        new PathSearch({el:'#fixed-topB-1-1'});
        new PathwaysList({el:'#rowA-1-1'});
        new ActionList({el:'#floating-right'});
        new TreeView({el:'#rowA-1-2'})

    },
    showNewPathway: function () {
        console.log('show New Pathway');
    },
    defaultAction: function (action) {
	    console.log('No route:', action);
	},
    initialize: function(){
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            options.url = 'pathway_services' + options.url;
        });

        Backbone.history.start();
    }
});
    return AppRouter;
});