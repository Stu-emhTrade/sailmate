var fs = require('fs')
var FromPgn = require('@canboat/canboatjs').FromPgn
var PGNparser = new FromPgn()
var ndjson = require('ndjson');

var inputStream = fs.createReadStream("./rawLog.ndjson");
var outputStream = fs.createWriteStream('./parsedLog.ndjson', {
  flags: 'a' // 'a' means appending (old data will be preserved)
})

var transformStream = inputStream.pipe( ndjson.parse() );

function makeCanDump2(json) {
  var timestamp = '('+ json.ts_sec + '.' + json.ts_usec + ')';
  var canID = json.id.toString(16);
  var buf = json.data.data.map( d => d.toString(16)).join(' ');
  
  return('can0 ' + canID + ' [8] ' + buf)
}

PGNparser.on('error', (pgn, error) => {
      console.error(`Error parsing ${pgn.pgn} ${error}`)
      console.error(error.stack)
    })

PGNparser.on('pgn', (pgn) => {
  outputStream.write(JSON.stringify(pgn) + '\n');
    })

transformStream.on("data", (data) => {
    //console.log(makeCanDump3(data));
      PGNparser.parseString(makeCanDump2(data));
    })