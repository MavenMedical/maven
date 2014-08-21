/* A Complex Backbone View which renders the detail editor and creator for all possible detail types based only on the
     contents oftheir Edit templates

   params:
        model           : the model of the detail to be edited, if a new detail is being created this will be a
                          new Backbone.Model()
        newDetail:      : will contain a value which is boolean true if the detail is new and undefined or false if
                          it is an old one to be edited
        el              : the location in which to render the view, will tend to be the modal target
        template        : the edit template for the detail to be created/edited
        type            : this is now loaded dynamically from the template and type is no longer needed





 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'Helpers',
    'internalViews/detailSearchBox',
    'internalViews/multiSelectSearch',
    'internalViews/routeListBox',
    'models/ruleModel'


], function ($, _, Backbone, Helpers, detailSearchBox, multiSelectSearch, routeListBox, curRule) {

    var DetailEditor = Backbone.View.extend({


        initialize: function(param){
            //load the params
            this.model = param.model;
            this.newDetail = param.newDetail
            this.$el = param.el;
            this.template = param.template
            this.type = param.type;

            this.$el.html(this.template());
            //an array representing all of the search boxes, so that on exit we can check if they have all been filled
            //out and prevent people from submitting incomplete rules
            //unused in current implementation which uses the multiselect search
            this.searchBoxes =[];
            var that = this

            //for each div with class search in the template render a single select detail search box, no templates
            //currently use this
            var searchEl = $('.search', this.$el)

            if (searchEl.length!=0){
                //create a new collection to represent the available options which will be returned by search
                var anon =  Backbone.Collection.extend( {url: '/search'})
                var col = new anon()
                if (!that.newDetail){
                    col.add(that.model)
                }
                // this is the only place where type is used, this should be changed to load dynamically from the
                // database
                var searchBox = new detailSearchBox({collection: col, type: this.type, el: searchEl})
                searchBox.render();
                this.searchBoxes.push(searchBox)
            }

            //for each div with class multi-select search create a multiSelectSearchPanel and render it in the div
            var multiSearchEl = $('.multi-select-search', this.$el)
            $.each(multiSearchEl, function(a, cur){

                //create a new Backbone Collection representing the available concepts in the 'availale' panel
                //giving it a url makes it searcahble
                var anon =  Backbone.Collection.extend( {url: '/search'})
                var avail = new anon
                //create a new backbone collection representing the currently selected items in the 'selected' panel
                //it starts out empty
                var sel = new Backbone.Collection()
                //if this is not a new detail, load its values of the type requested by this multiSelectEl
                //into the 'sel' collection
                if (!that.newDetail){
                    for (a in that.model.get(cur.getAttribute('name'))){
                        console.log(that.model)
                        var c = that.model.get(cur.getAttribute('name'))[a]
                        var t = that.model.get(cur.getAttribute('name')+'term')[a]
                        sel.add(new Backbone.Model({id: c, code: c, term: t, type: cur.getAttribute("type") }))
                    }
                }

                //create the multi select search box
                var searchBox = new multiSelectSearch({avail: avail, type: cur.getAttribute("type"), el: cur, selected: sel})
            })

            //create routeList views for each div in the template with class route-list
            var routeListEl = $('.route-list', this.$el)
            $.each(routeListEl, function(a, cur){
                var listBox = new routeListBox({el: cur})
            })
            //if this is an edited detail fill all of the normal input boxes with the correct values
            if (!this.newDetail){
                this.fillTemplate();
            }
            //show the el
            this.$el.show();


            var panel = this;

            //when the confirm detail button is pressed
            $('.confirm-detail-button', this.$el)[0].onclick = function(){
                //if any search box isnt complete, dont exit, give a warning, prevent creating a glitched detail
                if (panel.searchBoxes.length>0){
                    for (var cur in panel.searchBoxes){
                        if (!panel.searchBoxes[cur].ready){
                            alert("Constraint is not complete, make sure you have a value selected in all search boxes")
                            return;
                        }
                    }
                }
                //for each element in the template with class '.detail-input' update the value of the attribute with
                //the name of that element to to value of that element
                var inputs = $('.detail-input', panel.$el);
                for (var i=0;i<inputs.length;i++){
                    var cur = inputs[i];

                    //if the detail-input has the class has term, we know that it has a term as well as a value
                    //so, its also a search box, so loop through the box to find the selected one find its term
                    //and set it in the model


                    if ($(cur).hasClass('hasTerm')){

                        _.each(cur, function(current){
                            if (current.selected){
                                _.each(current.attributes, function(curAttrib){
                                    panel.model.set(curAttrib.name, curAttrib.value);
                                })
                            }
                        })
                    }
                    panel.model.set(cur.getAttribute('name'), cur.value);


                }

                //for each multi select search create the list of selected ids and their corresponding terms, and set
                //the value of the attribute in the model which has that name, to the id list, and the
                //value of the attribute in the model which is created by the name + "term" to the term list
                var multi = $('.multi-select-search', this.$el)
                _.each(multi, function(cur){
                    var selectedItems = $('.selected-items option', cur)
                    //instantiate the list
                    var idList = [];
                    var termList = []
                    _.each(selectedItems, function(cur){
                        //loop through the selected items and push their value to the id list,

                        idList.push(cur.value)
                        //push their term attribute to the term list
                        termList.push(cur.getAttribute("term"));
                    })
                    //set the model's attribute with the name of this multi-select-search to the id list
                    panel.model.set(cur.getAttribute('name'), idList);
                    //set the models attribute with the name of this multi-select-search concatenated with the string
                    // "term" to be the term list

                    panel.model.set(cur.getAttribute('name')+'term', termList);
                }, this)

                //if the panel is a new detail we need to add it to the rule. otherwise the changes have already been
                // made
                if (panel.newDetail){
                    //if cur rule alredy has details of this type, add the model in the panel to the preexisting
                    // collection
                    if (curRule.get(panel.type)){
                        curRule.get(panel.type).add(panel.model);
                    } else {
                    //if the cur rule doesnt have a detail of this type, make a new collection representing details of
                    //this type in the rule, and add this model to it
                        var model = new Backbone.Collection();

                        model.add(panel.model);
                        curRule.set(panel.type, model);

                    }
                    //incrment the persistant detail ID of the rule so that each detail can be assigned a unique id
                    curRule.set({detID: curRule.get('detID') + 1}, {silent:true})
                    //set the detail id of this rule to the newly incremented value which is guarenteed to be unique
                    panel.model.set({did: curRule.get('detID')});

                }
               //hide the detail modal
               $('#detail-modal').modal('hide');
               //tell the curRule that it needs to be updated in persistance
                curRule.needsSave = true;
                curRule.trigger("needsSave")
            }

            //when the cancel button is pressed just hide the editor
            $('.cancel-edit-button', this.$el)[0].onclick = function(){
                $('#detail-modal').modal('hide');
            }

        },
        //called if the rule is not a new rule, fill all of the normal input fields to have the value currently stored
        //in the model
        fillTemplate: function(){
            var inputs = $('.detail-input');
             for (var i=0;i<inputs.length;i++){
                    var cur = inputs[i];
                    cur.value = this.model.get(cur.name);

                }
        }






    });


    return DetailEditor;

});
