define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!../Templates/ListBoxEntry.html',
    'text!../Templates/TriggerListBox.html',
], function ($, _, Backbone, ListEntryTemplate, ListTemplate) {

    var RuleOverviewView = Backbone.View.extend({

        ListEntryTemp: _.template(ListEntryTemplate),
        ListTemp:_.template(ListTemplate),
        //Collection is Type: TriggerSet(),

        initialize: function(params){
            console.log(params);
            this.el = params.el;
            this.panelName = params.panelName;
            this.collection = params.collection;
            this.collection.on('add', function(){
                this.render();

            }, this)
            this.collection.on('remove',function(){
                this.render();
            }, this)
        },
        render: function(){

            var ListText="";
            this.collection.each(function(cur){
                //cur is a Trigger
                var entry;
                var id = cur.get('id');

                var desc= cur.get('code');
                entry = this.ListEntryTemp({triggerID: id, triggerDescription:desc});
                ListText +=entry;

            }, this)

            this.$el.html(this.ListTemp({listBoxHTML: ListText, id: this.panelName}));
        }

        });


    return RuleOverviewView;


});
