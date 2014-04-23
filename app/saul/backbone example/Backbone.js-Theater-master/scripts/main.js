
var Theater = {
    Models: {},
    Collections: {},
    Views: {},
    Templates:{}
};


Theater.Models.Movie = Backbone.Model.extend({});

Theater.Collections.Movies = Backbone.Collection.extend({
    model: Theater.Models.Movie,
    url: "scripts/data/movies.json",
    initialize: function(){
       console.log("Movies initialize");
    }
});


Theater.Templates.movies = _.template($("#tmplt-Movies").html());
Theater.Views.Movies = Backbone.View.extend({
    el: $("#mainContainer"),
    template: Theater.Templates.movies,
    //collection: new Theater.Collections.Movies(), //Not needed

    initialize: function () {
        _.bindAll(this, "render", "addOne", "addAll");
        this.collection.bind("reset", this.render);
        this.collection.bind("add", this.addOne);
    },

    render: function () {
        console.log("render");
        console.log(this.collection.length);
        $(this.el).html(this.template());
        this.addAll();
    },

    addAll: function () {
        console.log("addAll");
        this.collection.each(this.addOne);
    },

    addOne: function (model) {
        console.log("addOne");
        view = new Theater.Views.Movie({ model: model });
        $("ul", this.el).append(view.render());
    }

});

Theater.Templates.movie = _.template($("#tmplt-Movie").html());
Theater.Views.Movie = Backbone.View.extend({
    tagName: "li",
    template: Theater.Templates.movie,

    initialize: function () {
        _.bindAll(this, 'render');
    },

    render: function () {
        //return this.template(this.model.toJSON());

        //Correction
        return $(this.el).append(this.template(this.model.toJSON())) ;
    }
});


Theater.Router = Backbone.Router.extend({
    routes: {
        "": "defaultRoute" //http://localhost:22257/Theater/theater.htm
    },

    defaultRoute: function () {
    console.log("defaultRoute");
    Theater.movies = new Theater.Collections.Movies();
    new Theater.Views.Movies({ collection: Theater.movies });
    Theater.movies.fetch();
    console.log(Theater.movies.length);
}
});



var appRouter = new Theater.Router();
Backbone.history.start();
var movies = new Theater.Collections.Movies();

new Theater.Views.Movies({ collection: movies }); //!!!! Add this line
movies.fetch();

$("#butAddItem").click(null, function () {
    var movie = new Theater.Models.Movie(
        {
            "Id": "BVP3s",
            "Name": "Lord of the Rings ",
            "AverageRating": 4.3,
            "ReleaseYear": 2003,
            "Url": "http://www.netflix.com/.....",
            "Rating": "PG-13"
        }
    );

    Theater.movies.add(movie);
    console.log(Theater.movies.length)
});
