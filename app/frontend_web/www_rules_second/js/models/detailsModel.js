define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel',
    'models/ruleModel'
], function($, _, Backbone, contextModel, curRule){
    var DetailsModel = Backbone.Model.extend({


        initialize: function(){
            this.loadGroups()
        },
        loadGroups: function(){
            this.set({groups: new Backbone.Collection});
            for (var key in curRule.attributes){

                if (key!="name" && key!="id" && key!="triggers"){
                    this.get('groups').add(key);
                }

            }
        }


    });

    var detailsModel = new DetailsModel
    curRule.on('change', function(){
       detailsModel.loadGroups();
    }, detailsModel)

    return detailsModel;


});