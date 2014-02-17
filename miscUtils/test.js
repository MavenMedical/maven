var http = require('http');
var pg = require('pg');
var fs = require('fs');
var index = fs.readFileSync('index.html');
function answerSet(Name){
    this.list = [];
                this.Name = Name
		this.add = function(ans){
                    this.list.push(ans);
                }
                this.getAnswerByID = function(ID){
                    return this.list[ID];
		}
		this.setIncludeByID = function(ID, include){
		    this.list[ID].include = include;
		}
		this.setDiffByID = function(ID, diff){
		    this.list[ID].difficulty = diff;
		}

}
function answer(ID, include, difficulty){
    this.ID = ID;
    this.include = include;
    this.difficulty = difficulty;
}

function updateFromModel(model){
    console.log("updating from model");
    qd = "delete from maven_query1 * where doctor = '"+model.Name+"'";
    q1 = "insert into maven_query1 values ('"+model.Name+"', 'useCriterion'";
    q2 = "insert into maven_query1 values ('"+model.Name+"', 'difficulty'";
    for (var c=0;c<=263;c++){
	q1+=", '"+model.list[c].include +"'";
	q2+=", '" +model.list[c].difficulty+"'";
    }
    q1+=");";
    q2+=");";
    client = new pg.Client("postgres://azureuser:Maven010101@localhost:5432/maven");
    client.connect();
    qud = client.query(qd);
    qud.on('end', function(){
	    console.log("delete ended calling include");
	    qu1 = client.query(q1);
	    qu1.on('end',function(){
		    console.log("insert include done, calling insert difficulty");
		    qu2 = client.query(q2);
		    qu2.on('end', function(){
			    console.log("insert difficulty done, ending client");
			    client.end();
			});
		});
	});
    
    
}
var server = http.createServer(function (req, res) {
	if (req.method == 'GET'){
	    var body = '';
	    res.writeHead(200, {'Content-Type': 'text/html'});
	    res.end(index);
	} else {
	    var body = '';
	    req.on('data', function (data) {
			    body += data;
		});
	    req.on('end', function () {
       		    var data = JSON.parse(body);
		    console.log("post request sent containing " + data);
		    if (data.Name!='' &&  !data.Name){
				queryStr = "select * from maven_query1 where doctor = '"+data+"'";
				console.log("querying to obtain data");
				var newModel = new answerSet(data);
				console.log(newModel.Name);
				for (var counter =0;counter<=263;counter++){
				    newModel.add(new answer(""+counter, "",""));
					
				}
				console.log(newModel.list[263].ID);
				client = new pg.Client("postgres://azureuser:Maven010101@localhost:5432/maven");
				client.connect();
				var q = client.query(queryStr);
				q.on('row', function(row){
				for(var index = 0; index <=263;index++){
					    if (row['rtype'] == 'difficulty'){
						newModel.setDiffByID(index, row['q'+index]);
					    } else if (row['rtype'] == 'useCriterion'){
						newModel.setIncludeByID(index, row['q'+index]);
					    }
					}
				});
				q.on('end', function(){
					res.end(JSON.stringify(newModel));
					client.end();
				});
		    } else{
			console.log("about to update");
			updateFromModel(data);
			console.log("model update returned")
			res.end()
		    }
		});
	}
    });
// Listen on port 8000, IP defaults to 127.0.0.1
server.listen(8080);
// Put a friendly message on the terminal
console.log("Server running at http://127.0.0.1:8080/");
