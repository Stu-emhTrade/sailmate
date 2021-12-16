#!/usr/bin/env node

// imports
const readline = require('readline')
const toDeltaTransformer = require('@signalk/n2k-signalk/n2kMapper.js').toDeltaTransformer
const JSONStream = require('JSONStream')
const FromPgn = require('@canboat/canboatjs').FromPgn
const Stream = require('stream')
const fs = require('fs')

process.stdin.setEncoding('utf8');
process.stdout.setEncoding('utf8');

// create an interface to stdin/out
var rl = readline.createInterface({
  input: process.stdin
})
var outStream = process.stdout


// TESTING ONLY
// var rl = readline.createInterface({
//   input: fs.createReadStream("./test/actisenseTest")
// })
// var outStream = fs.createWriteStream("./test/signalkTestOutput")

// create a stream object
var readableStream = new Stream.Readable()
readableStream._read = () => {}

// create a parser object
var ActisenseParser = new FromPgn();

// tell it what to do when it has some output
ActisenseParser.on('error', (pgn, error) => {
  console.error(`Error parsing ${pgn.pgn} ${error}`)
  console.error(error.stack)
})

ActisenseParser.on('warning', (pgn, error) => {
  //console.error(`Warning parsing ${pgn.pgn} ${error}`)
})

ActisenseParser.on('pgn', (pgn) => {

  readableStream.push(JSON.stringify(pgn)) // write to stream
})


// read input and parse it
rl.on('line', function (line) {
  if ( line.length > 13 && line.charAt(13) === ';' ) {
    if ( line.charAt(14) === 'A' ) {
      ActisenseParser.parseString(line.substring(16))
    }
  } else {
    ActisenseParser.parseString(line)
  }
})

const state = {}

readableStream.pipe(JSONStream.parse())
    .pipe(toDeltaTransformer(null, state))
    .pipe(JSONStream.stringify(false))
    .pipe(outStream);