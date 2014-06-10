
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',

    'internalViews/detailGroup',
    'internalViews/detailSelector',

    'text!/templates/detailPanel/detailsOverview.html',
    'text!/templates/individualDetails/dxDetail.html'

], function ($, _, Backbone, contextModel, curRule, DetailGroup, DetailSelector, detailsOverviewTemplate, dxDetailTemplate) {




    var DetailOverview = Backbone.View.extend({

        template: _.template(detailsOverviewTemplate),
        lineTemplates: {'dx': dxDetailTemplate},
        detailHeadings: {'dx': "Problem List Diagnosis"},
        initialize: function(){

             curRule.on('sync', this.render, this)
             contextModel.on('change:showDetails', function(){
                 if (contextModel.get('showDetails')){
                     this.$el.show();
                 } else {
                     this.$el.hide();
                 }

             }, this)
             this.selector = new DetailSelector();
             this.selector.searchedDetails.on('sync', this.render, this);

        },
        render: function(){
                contextModel.set('showDetails', false)
                this.template = _.template(detailsOverviewTemplate);

                this.$el.html(this.template());

                for (var key in curRule.attributes){

                   if (key!="name" && key!="id" && key!="triggers"){
                        contextModel.set('showDetails', true);
                        var toTemplate = _.template(this.lineTemplates[key]);

                        var toHeading = this.detailHeadings[key];
                        var toList = curRule.get(key);

                        var cur = new DetailGroup({heading: toHeading, lineTemplate:toTemplate, list: toList})
                        $('.detail-sections', this.$el).append(cur.render().$el);

                    }

                }




                $(".detail-selector").html(this.selector.el.innerHTML);


            },

    searchDetails: function(){
        alert("do a search");





    },
	events: {
            "click #searchDetailsButton" : function(){
                this.selector.search();
            }
	        }
    });


    return DetailOverview;

});
