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
        _.each(Context.get('widgets'), function(cur){
                require(['widgets/'+cur[1], 'text!templates/'+ cur[2]], function(view, template){
                    var n = new view({template: template, el: cur[0]})
                })
        })
    },
    showNewPathway: function () {
        new TopBanner({el:'#fixed-topA-1-1'});
        new PathSearch({el:'#fixed-topB-1-1'});

    },
    defaultAction: function (action) {
	},
    initialize: function(){
        Context.setUser('tom', 'pw', '#');
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            options.url = 'pathway_services' + options.url;
        });
        Backbone.history.start();
    }
});
    return AppRouter;
});