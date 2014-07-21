define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'Views/TriggerListBoxView',
    'text!../Templates/TriggerListPanel.html',

], function ($, _, Backbone, TriggerListBoxView, TriggerListPanelTemplate) {

    var TriggerSelectorView = Backbone.View.extend({

        el: "#OverviewRuleEditTriggers",
        template: _.template(TriggerListPanelTemplate),


        // Model is Type: TriggerSelectorPanel,
        render: function(){
            var that = this;
            this.$el.html(this.template());
            var leftBox = new TriggerListBoxView({el: '#AvailTriggerListText',collection: this.model.get('AvailableTriggerSet'), panelName: "leftBox"});
            leftBox.render();

            var rightBox = new TriggerListBoxView({el: '#SelectedTriggerListText',collection: this.model.get('SelectedTriggerSet'), panelName: "rightBox"});

            rightBox.render();
            $('#addTriggerButton')[0].onclick = function(){

                var setToAdd = $('#leftBox option:selected');

                for (var c = 0; c<setToAdd.length; c++){

                    var val = setToAdd[c].value;
                    var toTransfer = that.model.get('AvailableTriggerSet').getTriggerByID(val);
                   that.model.get('SelectedTriggerSet').add(toTransfer);
                }


            };
            $('#removeTriggerButton')[0].onclick = function(){

                var setToRemove = $('#rightBox option:selected');

                for (var c = 0; c<setToRemove.length; c++){
                    var val = setToRemove[c].value;
                    var toTransfer = that.model.get('SelectedTriggerSet').getTriggerByID(val);
                      that.model.get('SelectedTriggerSet').remove(toTransfer);


                }


            };

        }

    });


    return TriggerSelectorView;


});
