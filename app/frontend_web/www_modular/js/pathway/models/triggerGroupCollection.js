define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel){


    var TriggerGroupCollection = Backbone.Collection.extend({
        initialize: function(JSON){
            var self = this
            if (JSON){
                for (var i in JSON){
                    var curGroup = JSON[i]

                    var t = new TriggerGroup({JSON: curGroup})
                    t.on('cascade', function(){ self.trigger('cascade')} )
                    this.add(t)
                }
            } else {
                var t = new TriggerGroup("or")
                t.on ('cascade', function(){ self.trigger('cascade')})
                this.add()
            }
            this.on('add', function(){self.trigger('cascade')})
            this.on('remove', function(){self.trigger('cascade')})

        },
        addGroup: function(relationship){
            var group = new TriggerGroup({relationship : relationship});
            this.add(group)
            return group
        }
    })

    var TriggerGroup = Backbone.Model.extend({
        initialize: function(param){
            var self = this
            if (param.JSON){
                this.set('relationship', param.JSON['relationship'])
                var t = new TriggerDetailTypes(param.JSON['details'])
                t.on('cascade', function(){ self.trigger('cascade')})
                this.set('details', t)
            } else if (param.relationship){
                this.set('relationship', param.relationship)
                var t = new TriggerDetailTypes()
                t.on('cascade', function(){ self.trigger('cascade')})
                this.set('details', t)
            }
            this.on('change', this.trigger('cascade'))

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
            var self = this

            for (var key in JSON){
                var value = JSON[key]
                var t = new TriggerDetailCollection(value)
                t.on('cascade', function(){self.trigger('cascade')})
                this.set(key, t)
            }
            this.on('change', self.trigger('cascade'))
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
            var self = this
            for (var i in JSON){
                var curDetail = JSON[i]
                var t = new TriggerDetail(curDetail)
                this.add(t)
            }
                //this.on('add', function(){this.trigger('cascade')})
                //this.on('remove', function(){this.trigger('cascade')})
            this.on('change', self.trigger('cascade'))
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
