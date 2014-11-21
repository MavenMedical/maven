define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel){


    var TriggerGroupCollection = Backbone.Collection.extend({

        populate: function(JSON, protocolVersion){
            var self = this
            if (protocolVersion == "version1"){
                for (var i in JSON){
                    var curGroup = JSON[i]

                    var t = new TriggerGroup()
                    t.populate({JSON: curGroup})
                    t.on('cascade', function(){ self.trigger('cascade')} )
                    this.add(t, {silent: true})
                }
            } else if (protocolVersion == "preversion"){
                var t = new TriggerGroup()
                t.populate({relationship : "and"})

                t.on ('cascade', function(){ self.trigger('cascade')})

                var temp = new TriggerDetailTypes()
                temp.populate(JSON)
                t.set('details', temp, {silent: true})

                this.add(t, {silent: true})
            }
            this.on('add', function(){self.trigger('cascade')})
            this.on('remove', function(){self.trigger('cascade')})

        },
        addGroup: function(relationship){
            var group = new TriggerGroup();
            group.populate({relationship : relationship})
            this.add(group)
            return group
        }

    })

    var TriggerGroup = Backbone.Model.extend({
        populate: function(param){
            var self = this
            if (param.JSON){
                this.set('relationship', param.JSON['relationship'])
                var t = new TriggerDetailTypes()
                t.populate(param.JSON['details'])
                t.on('cascade', function(){ self.trigger('cascade')})
                this.set('details', t, {silent: true})
            } else if (param.relationship){
                this.set('relationship', param.relationship, {silent: true})
                var t = new TriggerDetailTypes()
                t.populate();
                t.on('cascade', function(){ self.trigger('cascade')})
                this.set('details', t, {silent: true})
            }
            this.on('change', this.trigger('cascade'))

        },
        addDetail: function(model, type){
            var self = this;
              var enhancedModel = new TriggerDetail()
              enhancedModel.populate(model.attributes)
              enhancedModel.on('cascade', function(){self.trigger('cascade')})
              var detailGroup = this.get('details')

              if (detailGroup.get(type)){
                  detailGroup.get(type).add(enhancedModel)
              } else {
                  var temp = new TriggerDetailCollection()
                  temp.on('cascade', function(){self.trigger('cascade')})

                  temp.add(enhancedModel)
                  detailGroup.set(type, temp)
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
        populate: function(JSON){
            var self = this

            for (var key in JSON){
                var value = JSON[key]
                var t = new TriggerDetailCollection()
                t.populate(value)
                t.on('cascade', function(){self.trigger('cascade')})
                this.set(key, t, {silent: true})
            }
            this.on('change', function(){self.trigger('cascade')})
        },
        toJSON: function(){
            var ret = {}
            for (var key in this.attributes){
                var value = this.attributes[key]

                ret[key] = value.toJSON();
            }
            return ret;
        }
    })
    var TriggerDetailCollection = Backbone.Collection.extend({
        populate: function(JSON){
            var self = this
            for (var i in JSON){
                var curDetail = JSON[i]
                var t = new TriggerDetail()
                t.on('cascade', function(){self.trigger('cascade')})
                t.populate(curDetail)
                this.add(t, {silent: true})
            }
                this.on('add', function(){self.trigger('cascade')})
                this.on('remove', function(){self.trigger('cascade')})
        }
    })
    var TriggerDetail = Backbone.Model.extend({

        populate: function(JSON){
            var self = this
            for (var key in JSON){
                var value = JSON[key]
                this.set(key, value, {silent: true})
            }
            this.on('change', function(){self.trigger('cascade')})
        }

    })

    return TriggerGroupCollection

});
