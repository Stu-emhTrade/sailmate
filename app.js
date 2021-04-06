var fs = require('fs')
var can = require('socketcan');

var channel = can.createRawChannel("can0", true);
var logger = fs.createWriteStream('./rawLog.ndjson', {
  flags: 'a' // 'a' means appending (old data will be preserved)
})
var message = {};
// Log any message
channel.addListener("onMessage", (msg) => { 
  logger.write(JSON.stringify(msg) + '\n');
//  console.log(JSON.stringify(msg));
  }
 );

channel.start();


