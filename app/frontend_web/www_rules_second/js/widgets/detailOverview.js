
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',

    'internalViews/detailGroup',
    'internalViews/detailSelector',


    'Helpers',
    'text!/templates/detailPanel/detailsOverview.html',
    'text!/templates/individualDetails/dxDetail.html',
    'text!/templates/detailPanel/detailSection.html'

], function ($, _, Backbone, contextModel, curRule, DetailGroup, DetailSelector, Helpers, detailsOverviewTemplate, dxDetailTemplate, detailSection) {
    var createDetail = function(){
        var selected = $('.detail-selector').val();
        console.log(selected);
        if (selected == Helpers.detailHeadings['pl_dx']){
            var new_pl_dx = new Backbone.Model({'negative':true, 'code': '0'});
            require(['modalViews/' + 'pl_dx' + '_editor.js'],
		       function(modalView) {
		    	    var curView = new modalView({model: new_pl_dx, el:$('#modal-target'), newDetail: true});
		        }
            );
        }
    }
    var DetailOverview = Backbone.View.extend({

        template: _.template(detailsOverviewTemplate),
        lineTemplates: {'pl_dx': dxDetailTemplate},

        initialize: function(){

             curRule.on('sync', this.render, this)
             curRule.on('change', this.render, this)
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

                this.template = _.template(detailsOverviewTemplate);

                this.$el.html(this.template());
                $('.detail-sections', this.$el).hide();
                for (var key in curRule.attributes){

                   if (key!="name" && key!="id" && key!="triggers"){
                        $('.detail-sections', this.$el).show()
                        var toTemplate = _.template(this.lineTemplates[key]);
                        var toHeading = Helpers.detailHeadings[key];
                        var toList = curRule.get(key);
                        if (toList.length!=0){
                            var sectionTemplate = _.template(detailSection);
                            $('.detail-sections', this.$el).append(sectionTemplate({heading:toHeading}));
                            var cur = new DetailGroup({el: $('.items', this.$el).last(), lineTemplate:toTemplate, list: toList, type: key})
                            cur.render();
                        }
                    }
                }
                $(".detail-selector").html(this.selector.el.innerHTML);


            },


	events: {
            "click #searchDetailsButton" : function(){

                this.selector.search($('#detailSearch').val());
            },
            "click #addDetailButton": createDetail
	        }
    });


    return DetailOverview;

});
