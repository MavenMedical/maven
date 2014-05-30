define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'ScreenModels/RuleListDisplay',
    'text!../Templates/OverviewRuleList.html',
    'text!../Templates/ListEntry.html'

], function ($, _, Backbone, RuleListDisplay, rTemplate, ListEntryTemplate) {

    var RuleList = Backbone.View.extend({

        el: "#OverviewRuleList",
        template: _.template(rTemplate),
        model: new RuleListDisplay(),

        initialize: function(param){
            if (param.model){
                this.model =  param.model;
            }
        },
        render: function(){
            var that = this;
            var deleteRow = function(toDelete){
                that.model.deleteRule(toDelete);
                that.render();

            }
            var editRow = function(toEdit){

            }
            var html = this.template({});
            this.$el.html(html);
            $("#addRuleButton").on('click', function(){

                that.model.addRule("rule333");
                that.render();

            });
            var tempView = Backbone.View.extend({
                el: "#ListText",

                render: function(){
                    this.$el.html("");
                    this.$el[0].style.fontSize="200%";
                    this.collection.each(function(cur){

                        var anonItemView = Backbone.View.extend({
                            template: _.template(ListEntryTemplate),

                            render: function(){
                                var myModel = this.model;

                                this.$el.html(this.template({listText: this.model.get('myName')}));
                                this.$el.children().children()[0].onclick = function(){
                                    editRow(myModel);
                                }
                                this.$el.children().children()[1].onclick = function(){
                                    deleteRow(myModel);
                                }


                            }

                        });
                        var tempItemView = new anonItemView({model: cur});
                        tempItemView.render();
                        this.$el.append(tempItemView.$el);

                    }, this)

                    console.log();


                }

            })

            var listView = new tempView({collection: this.model.get('myRuleSet')});
            listView.render();
        }

    });


    return RuleList;


});
