var fs = require('fs')
var fromPgnStream = new (require('@canboat/canboatjs/lib/fromPgnStream2'))();
var readline = require('readline')
var n2kMapper = require('@signalk/n2k-signalk/n2kMapper.js');

var JSONStream = require('JSONStream');
var ndjson = require('ndjson');

var { Transform } = require('stream');

var toStringTr = new Transform({
  objectMode: true,

  transform(chunk, encoding, callback) {
    this.push(JSON.stringify(chunk) + "\n");
    callback();
  }
});

inputStream = fs.createReadStream("./src/logData/actisenseTest")

outputStream = fs.createWriteStream("./src/logData/pgnTest")
inputStream.on('data', (d)=>{console.log(fromPgnStream._transform(d,'utf8',()=>{return('done')}))})

inputStream.pipe(fromPgnStream)
fromPgnStream.pipe(toStringTr).pipe(outputStream)

var bob = 

inputStream.on('data',(d)=>{console.log(d.toString())})

fromPgnStream._transform("heleoo",'utf8',()=>{return('done')})

var ActisenseParser = new FromPgn();

ActisenseParser.on('error', (pgn, error) => {
  console.error(`Error parsing ${pgn.pgn} ${error}`)
  console.error(error.stack)
})

ActisenseParser.on('warning', (pgn, error) => {
  //console.error(`Warning parsing ${pgn.pgn} ${error}`)
})

ActisenseParser.on('pgn', (pgn) => {
  console.log(JSON.stringify(pgn))
})



var rl = readline.createInterface({
  input: fs.createReadStream("./src/logData/actisenseTest"), //revert to stdin if piped from python, or collect from an Arg
  output: fs.createWriteStream("./src/logData/TestOutput"),
  terminal: true
})



//rl.on('line', (line)=>{console.log('received: ${line}');})

rl.on('line', function (line) {
  if ( line.length > 13 && line.charAt(13) === ';' ) {
    if ( line.charAt(14) === 'A' ) {
      ActisenseParser.parseString(line.substring(16))
    }
  } else {
    ActisenseParser.parseString(line)
  }
})

#open the actisense file (or stdin dumped from python)


#pipe it to canboatjson conversion
inputStream.pipe(ActisenseParser.parseString()).pipe(process.stdout)

#pipe it to signalk conversion

#pipe it to signal k file (or stdout to be consumed by python)
inputStream.pipe(process.stdout)

process.inputStream.setEncoding('utf8');

const state = {}

inputStream.pipe(JSONStream.parse()).pipe(n2kMapper.toDeltaTransformer(null, state)).pipe(JSONStream.stringify(false)).pipe(process.stdout);