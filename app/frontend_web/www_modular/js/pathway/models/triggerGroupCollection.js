define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function ($, _, Backbone, contextModel) {

    //large nested model of triggers also used to describe implications applied to internal nodes

    //at the top level we have a Backbone collection of models for each group of triggers
    var TriggerGroupCollection = Backbone.Collection.extend({
        //do different things with the data depending on the version of the protocol being read, used for backawards
        //compatibility
        populate: function (JSON, protocolVersion) {
            var self = this
            if (protocolVersion == "version1") {
                for (var i in JSON) {
                    //for each group in the json parse out backbone models and collections
                    var curGroup = JSON[i]

                    var t = new TriggerGroup()
                    t.populate({JSON: curGroup})

                    this.add(t, {silent: true})
                }
            } else if (protocolVersion == "preversion") {
                var t = new TriggerGroup()
                t.populate({relationship: "and"})

                var temp = new TriggerDetailTypes()
                temp.populate(JSON)
                t.set('details', temp, {silent: true})

                this.add(t, {silent: true})
            }
            //the cascade function is how this collection notifies the tree that a save and rerender is needed
            //cascades travel up the model to this object which the global curTree is always listening to

            //call cascade when a group is added
            this.on('add', function () {
                self.trigger('cascade')
            })
            //call cascade when a group is removed
            this.on('remove', function () {
                self.trigger('cascade')
            })

            //if there are no groups in this model create a new empty group
            if (self.models.length == 0) {
                self.addGroup("and")
            }

        },
        //add a group with the given relationship
        addGroup: function (relationship) {
            var group = new TriggerGroup();
            var self = this;
            group.populate({relationship: relationship})

            this.add(group)
            return group
        }

    })
    //A model representing a single group, has a details field,representing all details
    //and a relationship field, representing the required relationship between them
    var TriggerGroup = Backbone.Model.extend({
        //Trigger groups can be created from JSON fully encoding them
        populate: function (param) {
            var self = this
            if (param.JSON) {
                this.set('relationship', param.JSON['relationship'], {silent: true})
                //create a new trigger detail types object with a field for each type of detail in the group

                var t = new TriggerDetailTypes()
                t.populate(param.JSON['details'])
                //if the trigger detail types collection calls for a cascade, call a cascade on this object
                //because of the model/collection relationship,  this also calls cascade on the top level
                //trigger groups collection
                t.on('cascade', function () {
                        self.trigger('cascade')
                    }
                )
                //put it in the group's 'details' field
                this.set('details', t, {silent: true})
                //empty groups can also be created by passing a relationship
            } else if (param.relationship) {
                this.set('relationship', param.relationship, {silent: true})
                var t = new TriggerDetailTypes()
                t.populate();
                //if the trigger detail types collection calls for a cascade, call a cascade on this object
                //because of the model/collection relationship,  this also calls cascade on the top level
                //trigger groups collection
                t.on('cascade', function () {
                        self.trigger('cascade')
                    }
                )
                this.set('details', t, {silent: true})
            }
            this.on('change', function () {
                self.trigger('cascade')
            })

        },
        //add a new detail to the group
        addDetail: function (model, type) {
            var self = this;
            var enhancedModel = new TriggerDetail()
            enhancedModel.populate(model.attributes)
            //when this new detail cascades call cascade on the model
            enhancedModel.on('cascade', function () {
                self.trigger('cascade')
            })
            var detailGroup = this.get('details')
            //if the group already has a field for details of this type, add the new detail, otherwise create the field
            //then add the detail
            if (detailGroup.get(type)) {
                detailGroup.get(type).add(enhancedModel)
            } else {
                //create an empty collection under this field to add the new detail to
                var temp = new TriggerDetailCollection()
                //if this new trigger detial collection cascades, cascade to the top
                temp.on('cascade', function () {
                    self.trigger('cascade')
                })
                //add the new detail to the collection
                temp.add(enhancedModel)
                //and set the new field
                detailGroup.set(type, temp)
            }

        },
        toJSON: function () {
            var ret = {}
            ret['relationship'] = this.get('relationship')
            ret['details'] = this.get('details').toJSON()
            return ret;
        }
    })
    //This model has a field for each detail type contained in a group, said field contains a collection
    //of details of that type
    var TriggerDetailTypes = Backbone.Model.extend({
        populate: function (JSON) {
            var self = this

            for (var key in JSON) {
                var value = JSON[key]
                var t = new TriggerDetailCollection()
                t.populate(value)
                //if any of the detail collections need a cascade, cascade to the top
                t.on('cascade', function () {
                    self.trigger('cascade')
                })
                this.set(key, t, {silent: true})
            }
            //if a field is added or modified cascade to the top
            this.on('change', function () {
                self.trigger('cascade')
            })
        },
        toJSON: function () {
            var ret = {}
            for (var key in this.attributes) {
                var value = this.attributes[key]

                ret[key] = value.toJSON();
            }
            return ret;
        }
    })
    //simple collection for each detail type, contains a list of details of the type
    var TriggerDetailCollection = Backbone.Collection.extend({
        populate: function (JSON) {
            var self = this
            for (var i in JSON) {
                var curDetail = JSON[i]
                //make a new detail for each element we are parsing
                var t = new TriggerDetail()
                t.populate(curDetail)
                //and add it to the collection
                this.add(t, {silent: true})
            }
            //when a new detail is addded cascade to the top
            this.on('add', function () {
                self.trigger('cascade')
            })
            //when a detail is removed cascade
            this.on('remove', function () {
                self.trigger('cascade')
            })
        }
    })
    //model containing the attributes specific to a given detail type
    var TriggerDetail = Backbone.Model.extend({

        populate: function (JSON) {
            var self = this
            //fill the fields from the json
            for (var key in JSON) {
                var value = JSON[key]
                /*
                 if (value instanceof Array){
                 value = new Backbone.Collection(value)

                 value.on('add', function(){self.trigger('cascade')})
                 value.on('remove', function(){self.trigger('cascade')})
                 value.on('change', function(){self.trigger('cascade')})
                 }
                 */
                this.set(key, value, {silent: true})

            }
        }

    })

    return TriggerGroupCollection

});
