define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel){


    var TriggerGroupCollection = Backbone.Collection.extend({
        initialize: function(JSON){
            if (JSON){
                for (var i in JSON){
                    var curGroup = JSON[i]
                    this.add(new TriggerGroup({JSON: curGroup}))
                }
            } else {
                this.add(new TriggerGroup("or"))
            }

        },
        addGroup: function(relationship){
            var group = new TriggerGroup({relationship : relationship});
            this.add(group)
            return group
        }
    })

    var TriggerGroup = Backbone.Model.extend({
        initialize: function(param){
            if (param.JSON){
                this.set('relationship', param.JSON['relationship'])
                this.set('details', new TriggerDetailTypes(param.JSON['details']))
            } else if (param.relationship){
                this.set('relationship', param.relationship)
                this.set('details', new TriggerDetailTypes())
            }

        },
        toJSON: function(){
            var ret = {}
            ret['relationship'] = this.get('relationship')
            ret['details'] = this.get('details').toJSON()
            return ret;
        }
    })

    var TriggerDetailTypes = Backbone.Model.extend({
        initialize: function(JSON){
            for (var key in JSON){
                var value = JSON[key]
                this.set(key, new TriggerDetailCollection(value))
            }
        },
        toJSON: function(){
            var ret = {}
            for (var key in this.attributes){
                var value = this.attributes[key]
                ret[key] = value.toJSON();
            }
        }
    })
    var TriggerDetailCollection = Backbone.Collection.extend({
        initialize: function(JSON){
                for (var i in JSON){
                    var curDetail = JSON[i]
                    this.add(new TriggerDetail(curDetail))
                }
        }
    })
    var TriggerDetail = Backbone.Model.extend({
        initialize: function(JSON){
            for (var key in JSON){
                var value = JSON[key]
                this.set(key, value)
            }
        }

    })

    return TriggerGroupCollection

});
