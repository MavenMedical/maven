/**
 * Created by Asmaa Aljuhani on 8/6/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone,
    'models/contextModel',
    'models/treeModel',

    'widgets/topBanner',
    'widgets/pathwaySearch',
    'widgets/pathwaysList',
    'widgets/actionList',
    'widgets/TreeView',
], function ($, _, Backbone, Context, treeModel, TopBanner, PathSearch, PathwaysList, ActionList, TreeView) {

var AppRouter = Backbone.Router.extend({
    routes: {
        "" : 'showHome',

        "createpathway" : 'showNewPathway',
        //default
        'pathway/:num': 'showHome'
    },
    preloaded: function(n){
        Context.on('change:auth', function(){
                showHome(n)

        })
    },
    showHome: function(n){
        var that = this
        Context.on('change:auth', function(){
        _.each(Context.get('widgets'), function(cur){
                require(['widgets/'+cur[1], 'text!templates/'+ cur[2]], function(view, template){
                    var n = new view({template: template, el: cur[0]})

                })
        })

                    Context.once('rendered', function(){
                       Context.set('id', n)
                       treeModel.fetch()
                       that.route('pathway/:num', 'pathway', function(num){
                         Context.set('id', num)
                         treeModel.fetch()
                    })
                     treeModel.on('sync', function(){
                         console.log((treeModel))
                         that.navigate('pathway/' + treeModel.get('id'))

                     })
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