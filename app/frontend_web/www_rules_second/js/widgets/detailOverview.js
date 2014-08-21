/* A Backbone View which represents an overview of all of the details in the rules
   implements the detailGroup internal view




 */
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

    //function for creating details, to be called when the add detail button is clicked
    var createDetail = function(){
        //find the text in the detail selector
        var selected = $('.detail-selector').val();
        //map that text to the correct detail type
        var text_code = _.invert(Helpers.detailHeadings)[selected];
       //require the correct template
        require(['text!/templates/individualDetails/' + text_code + '_editor.html'],
            function(curTemplate) {
                  var newModel;
                    newModel = new Backbone.Model({});

                    var toTemplate = _.template(curTemplate);
                    //create and show a detail editor with a new model and the loaded template, new detail is true so it
                    // will recieve a new detail id and be added to persistance
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
            //if the rule changes, render this
             curRule.on('change', this.render, this)
            //make sure the widget is visible when a rule is selected
                 curRule.on('selected', function(){
                  this.$el.show()
              }, this)
             //if the rule is cleared hide this
              curRule.on('cleared', function(){
                 this.$el.hide()
              }, this)
            this.$el.hide();
            //create a detail selector dropdown for making new details
            this.selector = new DetailSelector({el: $('.detail-selector')});

             //this.selector.searchedDetails.on('sync', this.render, this);

        },
        render: function(){
                //write the heading
                $('.detail-sections').html("<div style='text-align: center; font-size: 240%'>Details</div>");
                //hide the heading, will remain invisible if no details are rendered
                $('.detail-sections', this.$el).hide();
                //for ALL of the attributes in cur rule
                for (var key in curRule.attributes){
                   //only proceed if the key is NOT in the set of attributes that arent details
                   if (Helpers.notDetail.indexOf(key)==-1){
                       //show the details, there are some
                        $('.detail-sections', this.$el).show()
                        var context = this;
                        //load this detail type's template
                        require (['text!/templates/individualDetails/' + key + 'Detail.html'], function(key) {return  function(curTemplate){
                            //load the list of details of this type
                            var toList = curRule.get(key);
                            //load this detail type's heading
                             var toHeading = Helpers.detailHeadings[key];
                             var toTemplate = _.template(curTemplate);

                            var sectionTemplate = _.template(detailSection);

                                        $('.detail-sections', context.$el).append(sectionTemplate({heading:toHeading}));

                                        //create a new detail group for this detail type, and send it the collection of details of this type
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
