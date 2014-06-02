define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'Models/Rule',

    'ScreenModels/RuleListDisplay',
    'ScreenModels/RuleOverview',
    'text!../Templates/OverviewRuleList.html',
    'text!../Templates/ListEntry.html'

], function ($, _, Backbone, Rule, RuleListDisplay, RuleOverview, rTemplate, ListEntryTemplate) {

    var RuleList = Backbone.View.extend({

        el: "#OverviewRuleList",
        template: _.template(rTemplate),
        model: new RuleListDisplay(),
        //Model type is RuleListDisplay
        initialize: function(param){
            if (param.model){
                this.model =  param.model;
            }
            var that = this;
            this.model.on('happened', function(){

               that.render();

            });

        },
        render: function(){
            var that = this;
            var deleteRow = function(toDelete){
                that.model.deleteRule(toDelete);
                if (that.model.get('myOverview').get('RuleOverview').get('curRule')==toDelete){
                    that.model.get('myOverview').set('RuleOverview', null);
                }
                    that.render();

            };
            var editRow = function(toEdit){
                console.log("edit row called")
                console.log(toEdit);
                that.model.get('myOverview').set('RuleOverview' ,new RuleOverview(toEdit));


            }
            var html = this.template({});
            this.$el.html(html);
            $("#addRuleButton")[0].onclick = function(){
                console.log("add rule activated by click?");
                that.model.addRule(new Rule());
                that.render();

            };
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
                }

            })

            var listView = new tempView({collection: this.model.get('myRuleSet')});
            listView.render();
        }

    });


    return RuleList;


});
