/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',

    'text!templates/GroupEditor.html',
    'text!templates/UserGroup.html',
    'text!templates/GroupNameRow.html'

], function ($, _, Backbone, contextModel, GroupEditorTemplate, GroupTemplate, GroupNameRow) {
    //A model representing the state of groups, connected to the database
    var GroupsCollection = Backbone.Collection.extend({
        //this is the url for syncing this model with the server
        URL: '/EMAIL_GROUP',
        //When the server gives us info in JSON form this is how we put in Backbone Model form,
        parse: function(JSON){
            for (var i in JSON){
                var cur = JSON[i]
                var curModel = new GroupModel()
                curModel.populate(cur)
            }

        },
        //when we send data to the server turn the data in the Backbone Model into the JSON to sync
        toJSON: function(){
               var convertedAttribs = this.attributes
               //if nessecary, the code to turn the attributes into valid json goes here


                return convertedAttribs
        }


    })
    var GroupModel = Backbone.Model.extend({

        populate: function(JSON){
            //JSON Should contain users:Array id:int name:String desc:String
            this.set(JSON)
        }


    })
    var GroupManager = Backbone.View.extend({
       template: _.template(GroupEditorTemplate),
       rowTemplate: _.template(GroupNameRow),
       initialize: function(){

           //create a model which will match the server
           this.model = new GroupsCollection()
           //fetch the data from the server
           this.model.fetch()

           //If the model changes, which this view will do, sync with the server
           this.model.on('change', this.model.save)
           this.model.on('add', this.model.save)
           this.model.on('remove', this.model.save)
           //Whenever we sync with the server, rerender the view
           this.model.on('sync', this.render)


       },
       render: function(){
            //Everything nessecary to display the current state of the model goes here as well as event handlers to
            //change it
            var that = this
            this.$el.html(this.template())

            var groupListEl = $('#groupNames', this.$el)
            var curGroupEl = $('#curGroup', this.$el)


            for (var i in this.model.models){
                var cur = this.model.models[i]
                var curGroupNameEl = $(this.rowTemplate(cur.attributes))
                $('.nameDiv', curGroupNameEl).on('click', function(){
                    that.curGroup = cur;
                    new GroupView(cur, curGroupEl)
                })
                $('.deleteDiv', curGroupNameEl).on('click', function(){
                    that.model.remove(cur)
                })
                groupListEl.append(curGroupNameEl)
            }
            if (that.curGroup){
                new GroupView(that.curGroup, curGroupEl)
            }
       }

    });

    var GroupView = Backbone.View.extend({
        template: _.template(GroupTemplate),
        initialize: function(groupModel, elIn){
            this.$el = elIn
            this.groupModel = groupModel


        },
        render: function(){
            this.$el.html(this.template(this.groupModel.attributes))

        }




    })

    return GroupManager;

});
