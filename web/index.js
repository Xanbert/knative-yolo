var express = require('express');
var multer = require('multer');
bodyParser = require('body-parser');
var mongoose = require('mongoose');
var Detail = require('./models/detail');
var image = require('./models/image');
var user_process = require('./models/user_process');
var dir = './uploads';
const sharp = require("sharp");
const fs = require("fs");
const path = require('path');
var ffmpeg = require('ffmpeg');
const fetch = require('node-fetch');

const app = express();
app.use("/static",express.static(path.join(__dirname, "static")));
app.use("/temp",express.static(path.join(__dirname, "temp")));
app.use("/output",express.static(path.join(__dirname, "output")));
const tempFolder = './temp/';
const outputFolder = './output/';
/*var upload = multer({ dest: 'uploads/' });*/
////redis 
mongoose.connect('mongodb://dev-mongodb:27017/comp4651',{ useNewUrlParser: true , useUnifiedTopology: true, user: "test", pass:"password"});

////redis 
var redis = require('redis');
const client = redis.createClient({
          host : "dev-redis-master"
          // no_ready_check: true,
          // auth_pass: "secretpassword",                                                                                                                                                           
});    


// Cache middleware used to get cached data only so is useless for this project 
function cache(req, res, next) {
	//console.log(req)
	console.log("cache")
	console.log(req.files[0].originalname)
  const { imgname } = req.files[0].originalname;

  client.get(req.files[0].originalname, (err, data) => {
  	//console.log(data)
    if (err) throw err;

    if (data !== null) {
    	console.log("redis success")//i use this to check whether success or not
       
    } else {
      next();
    }
  });
}
/////////////////////////// upload setting 
const MAX_SIZE = 512000;
var upload = multer({
	dest: './uploads/',
	storage: multer.diskStorage({


  destination: function (req, file, callback) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir);
    }
    callback(null, 'uploads');
  },
  limits:{
   fileSize: MAX_SIZE
  },
  filename: function (req, file, callback) 
  { callback(null, file.originalname );}

}),

/////////////////////  filter wrong file type

fileFilter: function(req, file, callback) {
  var ext = path.extname(file.originalname)
  if (ext !== '.png' && ext !== '.jpg' && ext !== '.gif' && ext !== '.jpeg'&& ext !== '.mp4'&& ext !== '.mov') {
    return callback(/*res.end('Only images are allowed')*/ null, false)
  }
  callback(null, true)
}
});


app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.use(express.static('uploads'));

////////main page
app.get('/',function(req, res){
	binimgfordata =[]
  ///////get data from mongodb start
  User_process.find({}, function(err,data){
  	console.log("mongodb data");
    console.log(data);
    if(err){
      console.log(err);
    }else{
      var names=[];
      var fileType=[];
    	for(i in data ){
       var tmp = splitstring(data[i].username);
       var name = tmp[0];
       var type = tmp[1];
       names.push(name);
       fileType.push(type);
    	 }
      res.render('index',{data:data,name:names,types:fileType,state:"showall"});
    }
  })
  ///////get data from mongodb end
  
});
var imgPath = './uploads/';

app.post('/', upload.any(), function(req,res){////cache used to get video from redis so i dont add it here 
  ///status to removed 
  var oldname = { username: req.files[0].originalname };
  var newpro = { $set: {username: req.files[0].originalname, status:"removed"} };
  User_process.updateMany(oldname,newpro,function(err,data){
    if(err) 
      console.log(err);
    else if(data.nModified > 0){
      console.log("update status");
      var schema_name = "user_"+req.files[0].originalname; 
      // var Images = mongoose.model('Image', image_Schema, schema_name);
      mongoose.connection.db.dropCollection(schema_name, function(err, result) {console.log("droppedss")});
    }
});
  //////////insert new
  var user_process = new User_process({
    username:req.files[0].originalname, //videoname 
    status: "submitted", 
    });
  user_process.save(function(err) {
    if(err) console.log(err);
  });
  data=fs.readFileSync(req.files[0].path); //get binary data
  client.set(req.files[0].originalname, data); //upload to redis

  console.log('uploaded to redis')
  //////////////////////request to knative-yolo 

var url ='http://yolo';
var headers = {
  "Content-Type": "text/plain",
  "Host": "yolo.yolo.example.com"
}
var data = req.files[0].originalname
fetch(url, { method: 'POST', headers: headers, body: data});

  ////////////////////upload to mongodb end testing only end
  res.redirect('/');
});

app.post('/delete',function(req,res){////delete data from mongodb

   User_process.findByIdAndRemove(req.body.prodId,function(err, data) {

    //console.log(data);

   })
  res
  .redirect('/');
});
////////////show specify collection
app.get('/:name', function(req, res) {
  console.log(req.params.name);
    binimgfordata =[];
    var param_name = req.params.name.replace('_','.');
 
    var schema_name = "user_"+param_name;
    var Images = mongoose.model('Image', image_Schema, schema_name); 
  var targetid="";
  // User_process.find({ username: param_name}, function(err,data){
  // //console.log("mongodb data");
  // //console.log(data);
  // if(err){
  //     console.log(err);
  //   }else{
  //      var user_process_name = data[i].username;
  //      if(user_process_name==param_name){
  //       targetid=data[i]._id;
  //       console.log(targetid);
  //      }
   
  //     //res.render('index',{data:data,name:names,state:"showall"});
  //   }
  // })
  Images.find({}, function(err,data){
    if(err){
      console.log(err);
    }else{
      var binimg =[]
      var data_array =[]
      for(i in data ){
          // if(data[i].userid==targetid){
          var str = 'data:image/jpeg;base64,'+ data[i].base64;  
          binimg.push(str);
          data_array.push(data[i])
          // }
       }
       res.render('index',{name:param_name,data:data_array,binimgfordata:binimg,state:"showone"});//pass result to index.ejs
    }
  })
});
const { spawn} = require('child_process');
const events = require('events');
var zip = require('bestzip');
const myEmitter = new events.EventEmitter();
var arrayofimage=[];
function splitstring(str){

  var res = str.split(".");
  return res;
}
function base64_encode(file) {//////i copied from web and not sure it works 
    // read binary data
    var bitmap = fs.readFileSync(file);
    // convert binary data to base64 encoded string
    return new Buffer(bitmap).toString('base64');
}
function base64_decode(base64str, file) {//////i copied from web and not sure it works 
    // create buffer object from base64 encoded string, it is important to tell the constructor that the string is base64 encoded
    var bitmap = new Buffer(base64str, 'base64');
    // write buffer to file
    fs.writeFileSync(file, bitmap);
    console.log('******** File created from base64 encoded string ********');
}

var port = 4000;
app.listen( port, function(){ console.log('listening on port '+port); } );
