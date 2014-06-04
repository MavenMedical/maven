define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!../Templates/ListBoxEntry.html',
    'text!templates/triggerListBox.html',
], function ($, _, Backbone, ListEntryTemplate, listBoxTemplate) {

    var RuleOverviewView = Backbone.View.extend({

        ListEntryTemp: _.template(ListEntryTemplate),
        listBoxTemplate:_.template(listBoxTemplate),

        initialize: function(params){


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
