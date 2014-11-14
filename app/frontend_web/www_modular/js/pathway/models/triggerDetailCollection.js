define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'pathway/models/nodeModel',
], function($, _, Backbone, contextModel, nodeModel){
    var triggerDetailCollection = Backbone.Collection.extend({

        initialize: function(detailListJSON){
            this.groups = new Backbone.Model(detailListJSON['groups'])
            this.curGroupID = detailListJSON['curGroupID']
            for (var key in detailListJSON['models']){
                var triggerDetail = new triggerDetail(detailListJSON[key])
                this.add(triggerDetail)
            }
        }
    })

    var triggerDetail = Backbone.Model.extend({

        initialize: function() {
            this.set(
                'group':
        },
    })
}