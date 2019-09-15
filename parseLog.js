var fs = require('fs')
var Parser = require('@canboat/canboatjs');
var ndjson = require('ndjson');

var inputStream = fs.createReadStream("./log.ndjson");
var transformStream = inputStream.pipe( ndjson.parse() );
var PGNparser = new Parser();

transformStream.on("data", (data) => {
  PGNparser.parseString(data);
})

PGNparser.on('error', (pgn, error) => {
      console.error(`Error parsing ${pgn.pgn} ${error}`)
      console.error(error.stack)
    })

PGNparser.on('pgn', (pgn) => {
      console.log(JSON.stringify(pgn))
    })
