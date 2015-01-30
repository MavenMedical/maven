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
        url: '/user_group/'

    })
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

            $('#addGroupButton', this.$el).on('click', function () {
                var newName = prompt("Please enter the new group name");
                if (newName) {
                    var newGroup = new GroupModel({users: [], term: newName, description: "handle later"})
                    newGroup.on('sync', function(){
                        that.model.fetch()
                    })
                    newGroup.save()
                }

            })

            $.each(this.model.models, function () {
                var cur = this
                var curGroupNameEl = $(that.rowTemplate(this.attributes))
                $('.nameDiv', curGroupNameEl).on('click', function () {
                    that.curGroup = cur;
                    new GroupView(cur.get('id'), curGroupEl)
                })
                $('.deleteDiv', curGroupNameEl).on('click', function () {
                    that.model.remove(cur)
                    var representModel = new GroupModel()
                    representModel.set('id', cur.get('id'))
                    representModel.on('destroy', function(){
                        that.model.fetch();
                    })
                    representModel.destroy()
                })
                groupListEl.append(curGroupNameEl)
            })

            if (that.curGroup) {
                new GroupView(that.curGroup.get('id'), curGroupEl)
            }
        }

    });

    var GroupView = Backbone.View.extend({
        template: _.template(GroupTemplate),
        initialize: function (groupID, elIn) {
            var that = this;
            this.$el = elIn

            this.groupModel = new GroupModel()
            this.groupModel.set('id', groupID)
            this.groupModel.on('sync', function () {
                that.render()
            })

            this.groupModel.fetch()


        },
        render: function () {
            var that = this;

            this.$el.html(this.template(this.groupModel.attributes))
            var selectEl = $('#selectionBox', this.$el)
            $.each(this.groupModel.get('users'), function () {
                var newEl = $("<option value='" + this.value + "'>" + this.label + "</option>")
                //add click handlers
                //append
                selectEl.append(newEl)
            })
            $('#removeButton', this.$el).on('click', function () {
                //remove the selected users from the group
                var value = $('#selectionBox', that.$el).val()
                for (var i in that.groupModel.get('users')){
                    var cur = that.groupModel.get('users')[i]
                    if (cur.value == value){
                        that.groupModel.get('users').splice(i, 1)
                    }

                }
                that.groupModel.save()
            })
            $(document).ready(function() {
                $('#user-field').autocomplete({
                    source: function (request, response) {
                        $.ajax({
                            url: "/users",
                            term: request.term,
                            dataType: "json",
                            data: $.param(contextModel.toParams()) + "&target_user=" + request.term + "&group=" + that.groupModel.get('id'),
                            success: function (data) {
                                response(data);
                            }
                        });
                    },
                    minLength: 3,
                    select: function (event, ui) {
                        event.preventDefault();
                        if (ui.item) {
                            $(event.target).val("");(ui.item.label);
                            $("#recipientUserName").val(ui.item.value);
                            var newUser = {value: ui.item.value, label: ui.item.label}
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
