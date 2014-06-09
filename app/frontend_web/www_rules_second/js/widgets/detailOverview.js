
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',

    'internalViews/detailGroup',

    'text!/templates/detailsOverview.html',
    'text!/templates/dxDetail.html'

], function ($, _, Backbone, contextModel, curRule, DetailGroup, detailsOverviewTemplate, dxDetailTemplate) {




    var DetailOverview = Backbone.View.extend({

        template: _.template(detailsOverviewTemplate),
        lineTemplates: {'dx': dxDetailTemplate},
        detailHeadings: {'dx': "Problem List Diagnosis Details"},
        initialize: function(){

             curRule.on('sync', this.render, this)
             contextModel.on('change:showDetails', function(){
                 if (contextModel.get('showDetails')){
                     this.$el.show();
                 } else {
                     this.$el.hide();
                 }

             }, this)
        },
        render: function(){
                contextModel.set('showDetails', false)
                this.template = _.template(detailsOverviewTemplate);
                this.$el.show();
                this.$el.html(this.template());
                console.log(curRule);
                for (var key in curRule.attributes){
                    console.log(curRule.attributes);
                   if (key!="name" && key!="id" && key!="triggers"){
                        contextModel.set('showDetails', true);
                        var toTemplate = _.template(this.lineTemplates[key]);

                        var toHeading = this.detailHeadings[key];
                        var toList = curRule.get(key);
                        console.log(toList);
                        var cur = new DetailGroup({heading: toHeading, lineTemplate:toTemplate, list: toList})
                        $('.detail-sections', this.$el).append(cur.render().$el);

                    }

                }

            },

	events: {

	        }
    });


    return DetailOverview;

});
