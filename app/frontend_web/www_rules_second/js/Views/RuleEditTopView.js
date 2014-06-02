define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'Models/Rule',
    'text!../Templates/OverviewRuleEditTop.html',

    'text!../Templates/ROListEntry.html'


], function ($, _, Backbone, Rule, rTemplate, ROListEntry) {

    var RuleEditTopView = Backbone.View.extend({

        el: "#OverviewRuleEditTop",
        template: _.template(rTemplate),
        listEntryTemp: _.template(ROListEntry),
        //Model is type, rule

        render: function(){

            this.$el.html(this.template({RuleName: this.model.get('myName')}));
            var that = this;
            $('#nameTag')[0].onclick = function(){
               var name = prompt('Enter the new name for the rule');
               if (name){
                   that.model.set('myName', name);
                   that.render();
               }


            };
            var TriggerView = Backbone.View.extend({
                el: '#TriggerList',
                initialize: function(){
                     this.collection.on('add', function(){
                        this.render();

                    }, this);

                    this.collection.on('remove', function(){
                        this.render();

                    }, this)

                 },
                render: function(){
                    this.$el.html("");


                    this.collection.each(function(cur){
                      this.$el.append(that.listEntryTemp({listText: cur.getDescription()}));

                    },this);

                }
            });
            var curView = new TriggerView({collection: this.model.get('myTriggers')});
           curView.render();

            $('#EditTriggersButton').on('click', function(){
                that.trigger('openEdit');


            });
        }

    });


    return RuleEditTopView;


});
