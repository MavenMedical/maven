/* a Backbone view for giving the user a list of detail types to choose from
    params:
          el    :the div in which to render the list
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'models/contextModel',


    'Helpers',
    'text!templates/detailPanel/detailChooserEntry.html'
], function ($, _, Backbone, contextModel, Helpers, detailEntry) {

    var DetailSelector = Backbone.View.extend({
        template: _.template(detailEntry),
        initialize: function(param){
            //load the params
            this.el = param.el;
            //Create a Backbone Collection to fetch the available detail types from the server, currently hard coded
            //intention is to allow filtering when the number of detail types becomes high

                this.searchedDetails =  new Backbone.Collection();
                this.searchedDetails.url = '/details?'


            //as soon as the user logs in load the detail types into the collection
            contextModel.on('change:auth', this.search(""), this);

        },

        search: function(search_param){
            var panel = this;
            var t = contextModel.toParams();
            t = $.extend(t , {'search_param': search_param});
            this.searchedDetails.fetch({data:$.param(t), success:function(){
                //when the detail types are loaded render the view
                panel.render();
            }})

        },
        render: function(){
            this.$el.html("");
            var entryTemplate = _.template(detailEntry);
            //for each detail type
            for (var i in this.searchedDetails.models){
                var cur = this.searchedDetails.models[i]
                //fetch the long descriptions and short names corresponding to the detailType code from the Helpers class and render the line
                this.$el.append(entryTemplate({id:cur.get('id'), desc:Helpers.detailDescriptions[cur.get('type')], type:Helpers.detailHeadings[cur.get('type')]}));

            }



        }
    })


    return DetailSelector;

});
