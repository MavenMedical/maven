
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',

    'internalViews/detailGroup',
    'internalViews/detailSelector',

    'modalViews/detailEditor',
    'Helpers',

    'text!/templates/detailPanel/detailsOverview.html',

    'text!/templates/detailPanel/detailSection.html'

], function ($, _, Backbone,
             contextModel, curRule,
             DetailGroup, DetailSelector, DetailEditor,
             Helpers,
             detailsOverviewTemplate,  detailSection) {
    var createDetail = function(){
        var selected = $('.detail-selector').val();
        var text_code = _.invert(Helpers.detailHeadings)[selected];
        require(['text!/templates/individualDetails/' + text_code + '_editor.html'],
            function(curTemplate) {
                  var newModel;
                    newModel = new Backbone.Model({});
                if (selected == Helpers.detailHeadings['pl_dx'])
                     newModel = new Backbone.Model({'negative':'false', 'code': '0'});
                  if (selected == Helpers.detailHeadings['hist_dx'])
                     newModel = new Backbone.Model({'negative':'false', 'code': '0', 'minDays':'0', 'maxDays': '0'});

                    console.log(toTemplate);
                    var toTemplate = _.template(curTemplate);
		    	    var curView = new DetailEditor({model: newModel, el:$('#modal-target'), newDetail: true, template: toTemplate, type: text_code});
                    $('#detail-modal').modal('show');

             }, this
        );
    }
    var DetailOverview = Backbone.View.extend({
        template: _.template(detailsOverviewTemplate),


        initialize: function(){
             this.$el.html(this.template());

             //curRule.on('sync', this.render, this)
             curRule.on('change', this.render, this)
             contextModel.on('change:showDetails', function(){
                 if (contextModel.get('showDetails')){

                     this.$el.show();
                 } else {
                     this.$el.hide();
                 }

             }, this)
             this.$el.hide();
            contextModel.set('showDetails', false);
            this.selector = new DetailSelector({el: $('.detail-selector')});

             //this.selector.searchedDetails.on('sync', this.render, this);

        },
        render: function(){
                $('.detail-sections').html("<div style='text-align: center; font-size: 240%'>Details</div>");

                $('.detail-sections', this.$el).hide();
                for (var key in curRule.attributes){
                   if (Helpers.notDetail.indexOf(key)==-1){
                        $('.detail-sections', this.$el).show()
                        var context = this;

                        console.log("key", key);
                        require (['text!/templates/individualDetails/' + key + 'Detail.html'], function(key) {return  function(curTemplate){
                             var toList = curRule.get(key);
                             var toHeading = Helpers.detailHeadings[key];
                             var toTemplate = _.template(curTemplate);
                                var sectionTemplate = _.template(detailSection);
                                        $('.detail-sections', context.$el).append(sectionTemplate({heading:toHeading}));
                                        var cur  = new DetailGroup({el: $('.items', context.$el).last(), lineTemplate:toTemplate, list: toList, type: key})
                                        cur.render();


                        };}(key));
                   }

                }
             //   $(".detail-selector").html(this.selector.el.innerHTML);


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
