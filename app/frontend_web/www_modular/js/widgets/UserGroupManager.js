/*
    This view/controller is designed to create and manage user groups, these groups could be used for many purposes
    at this time they can be used to filter the triggering of pathways and to set followup email recipients
    but the potential uses are innumerable

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
    //the group collection fetcges from the database with a GET the results are only the names of the groups
    //not their detailed info
    var GroupsCollection = Backbone.Collection.extend({
        url: '/user_group/'

    })
    //when a group is selected to be edited, we fetch group model by ID
    //this gives us the full model with all of the group's details
    var GroupModel = Backbone.Model.extend({
        url: function () {
            if (this.get('id')) {
                return '/user_group/' + this.get('id')
            } else {
                return '/user_group/'
            }
        }
    })
    var GroupManager = Backbone.View.extend({
        template: _.template(GroupEditorTemplate),
        rowTemplate: _.template(GroupNameRow),
        initialize: function () {
            var that = this
            //create a model which will match the server
            this.model = new GroupsCollection()


            //Whenever we sync with the server, rerender the view

            this.model.on('sync', function () {
                that.render()}
            )

            this.model.on('add', function () {
                that.render()
            })
            this.model.on('remove', function () {
                that.render()
            })
            //if the fetch fails, (server isnt ready), load the test set of groups
            this.model.on('error', function () {
                that.model.set([
                    {users: ['a', 'b'], id: 1, term: "test name", description: "test desc"}
                ], {silent: true})
                that.render()
            })
            this.model.fetch()


        },
        render: function () {
            //Everything nessecary to display the current state of the model goes here as well as event handlers to
            //change it
            var that = this
            this.$el.html(this.template())

            var groupListEl = $('#groupNames', this.$el)
            var curGroupEl = $('#curGroup', this.$el)

            //when the add group button is pressed
            $('#addGroupButton', this.$el).on('click', function () {
                var newName = prompt("Please enter the new group name");
                if (newName) {
                    //make a new group model
                    var newGroup = new GroupModel({users: [], term: newName, description: "handle later"})
                    //prepare to reload the list of groups when the new group is saved
                    newGroup.on('sync', function(){

                        that.model.fetch()
                    })
                    //save the new group, getting an ID
                    newGroup.save()
                }

            })


            //render the groups to be clicked
            $.each(this.model.models, function () {
                var cur = this
                //Build the element for this group in the collection
                var curGroupNameEl = $(that.rowTemplate(this.attributes))
                $('.nameDiv', curGroupNameEl).on('click', function () {

                    that.curGroup = cur;
                    //if the group name is clicked, make a new group view from the selected ID
                    new GroupView(cur.get('id'), curGroupEl)
                })
                //if the delete function is ordered, destroy the model and fetch the list again, rerendering
                $('.deleteDiv', curGroupNameEl).on('click', function () {

                    //sort of a round about way of doing it but.. create a model whose DELETE URL will order a delete
                    //of the specified item, could be done more elegently, but it works
                    var representModel = new GroupModel()
                    representModel.set('id', cur.get('id'))
                    representModel.on('destroy', function(){
                        that.model.fetch();
                    })
                    representModel.destroy()
                })
                //Append the created element to the list
                groupListEl.append(curGroupNameEl)
            })



            //if at the end of a render there is a group in curGroup, load it into the group editor spot
            if (that.curGroup) {
                new GroupView(that.curGroup.get('id'), curGroupEl)
            }
        }

    });
    //this view goes inside the group manager and is for controlling the single currently edited group
    var GroupView = Backbone.View.extend({
        template: _.template(GroupTemplate),

        //the constructor takes a groupID to create a model of, and an EL in which to render the view
        initialize: function (groupID, elIn) {
            var that = this;
            this.$el = elIn

            this.groupModel = new GroupModel()
            this.groupModel.set('id', groupID)
            //when the fetch completes render the view, also if it changes and forces a save
            this.groupModel.on('sync', function () {
                that.render()
            })
            //fetch the data for the desired group, triggering a render
            this.groupModel.fetch()


        },
        render: function () {
            var that = this;

            this.$el.html(this.template(this.groupModel.attributes))
            var selectEl = $('#selectionBox', this.$el)
            //for each user in the model create a selectable item in the list box
            $.each(this.groupModel.get('users'), function () {
                var newEl = $("<option value='" + this.value + "'>" + this.label + "</option>")
                //add click handlers
                //append
                selectEl.append(newEl)
            })


            //if the remove button is clicked
            $('#removeButton', this.$el).on('click', function () {
                //remove the selected users from the group
                var value = $('#selectionBox', that.$el).val()

                //remove the users with the desired value
                for (var i in that.groupModel.get('users')){
                    var cur = that.groupModel.get('users')[i]
                    if (cur.value == value){
                        that.groupModel.get('users').splice(i, 1)
                    }

                }
                //and update the model, has to be triggered manually because we used an array not a  backbone collection in the
                //model so we cant listen to change
                that.groupModel.save()
            })

            //autocomplete code for the search box, used to find users to add to the group
            $(document).ready(function() {
                $('#user-field').autocomplete({
                    source: function (request, response) {
                        $.ajax({
                            url: "/users",
                            term: request.term,
                            dataType: "json",
                            data: $.param(contextModel.toParams()) + "&target_user=" + request.term + "&group=" + that.groupModel.get('id'),
                            success: function (data) {
                                for (var i = 0; i < data.length; i++){
                                    data[i].value = data[i].user_id + "-" + data[i].value;
                                }
                                response(data);
                            }
                        });
                    },
                    minLength: 3,
                    //when a user is selected push the selected user to the group and save it, triggering a rerender
                    select: function (event, ui) {
                        event.preventDefault();
                        if (ui.item) {

                            var id = parseInt(ui.item.value.split('-')[0])
                            var value = ui.item.value.split('-')[1]
                            var newUser = {id:id, value: value, label: ui.item.label}

                            that.groupModel.get("users").push(newUser)
                            that.groupModel.save();
                           // var newEl = $("<option value='" + ui.item.value + "'>" + ui.item.label + "</option>")
                           // selectEl.append(newEl)
                        }
                    }
                });
            });
        }
    })

    return GroupManager;

});
