var fs = require('fs')
var can = require('socketcan');

var channel = can.createRawChannel("can0", true);
var logger = fs.createWriteStream('./log.txt', {
  flags: 'a' // 'a' means appending (old data will be preserved)
})

// Log any message
channel.addListener("onMessage", (msg) => { 
  logger.write(msg + '/n'); } );
  
  channel.addListener("onMessage", (msg) => { 
    logger.write(msg + '/n'); } );

