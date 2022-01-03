library(jsonlite)
library(ndjson)
library(DescTools)
library(BMS)
library(Rmpfr)
library(data.table)
library(leaflet)
library(htmltools)
setwd('~/documents/github/personal/sailmate')

backToRaw = function(l){
  l = fromJSON(l)
  timestamp = as.numeric(paste0(l$ts_sec,".",l$ts_usec))
  canId = l$id
  msg_header = decomp_id(canId)
  buf = paste(as.hexmode(l$data$data),
              sep = "",
              collapse = " ")
  
  output = data.table(timestamp = timestamp,
                      canId = canId,
                      priority = msg_header$priority,
                      source_id = msg_header$source_id,
                      destination = msg_header$destination,
                      pgn = msg_header$pgn,
                      dat = buf)
  return(output)
}


decomp_id = function(cid, output) {
  ### refactored from https://github.com/canboat/canboatjs/blob/master/lib/canId.js
  id = cid
  prio = bitwAnd( bitwShiftR(cid, 26) , 7)
  src_id = bitwAnd(cid, as.hexmode('ff'))
  
  pf = bitwAnd( bitwShiftR(cid, 16) , as.hexmode('ff'))
  ps = bitwAnd( bitwShiftR(cid, 8) , as.hexmode('ff'))
  dp = bitwAnd( bitwShiftR(cid, 24) , 1)
  
  if (pf < 240) {
    dst = ps
    pgn = bitwShiftL(dp, 16) + bitwShiftL(pf, 8) 
  }  else {
    dst = as.integer(as.hexmode('ff'))
    pgn = bitwShiftL(dp, 16) + bitwShiftL(pf, 8) + ps
  }
  
  tmp = (list(raw_id = id,
              priority = prio,
              source_id = src_id,
              destination = dst,
              pgn = pgn))
  
  return(switch(output,
                priority = tmp$priority,
                source = tmp$src_id,
                dest = tmp$destination,
                pgn = tmp$pgn))
}

for(i in 54000:length(test)){
  if(i ==1) {
    raw_dat = backToRaw(test[i])
  } else {
    raw_dat = rbind(raw_dat,backToRaw(test[i]))
  }
}


processFile = function(filepath_in,
                       directory_out, 
                       lines_per_file = 100000) {
  con = file(filepath_in, "r")
  total_lines = length(readLines(con))
  no_of_files = ceiling(total_lines / lines_per_file)
  con = file(filepath_in, "r")
  for ( f in 1:no_of_files ) {
    con2 = file(paste(directory_out,'/',
                      strsplit(filepath_in,'\\.')[[1]][1],
                      '_clean_',f,
                      '.ndjson',sep = ""),
                "w")
    linesToRead = ifelse(f == no_of_files, 
                         total_lines %% lines_per_file,
                         lines_per_file)
    l = 0
    while( l < linesToRead ) {
      line = readLines(con, n = 1)
      if (length(line) > 0) {
        if ( nchar(line) > 0 ) {
          if( validate(line) ) {
            # line_out = backToRaw(line)
            # outputTable <<- rbind(outputTable,line_out)
            writeLines(line,con = con2)
            l = l + 1
          }
        }
      } else {
        l = l + 1
        next
      }
    }
    close(con2)
  }
  close(con)
}

outputTable = data.table( timestamp = numeric(),
                          canId = integer(),
                          priority = integer(),
                          source_id = integer(),
                          destination = integer(),
                          pgn = integer(),
                          dat = character())

processFile(filepath_in = '20191031_rawLog.ndjson',
            directory_out = 'data_files',
            lines_per_file = 100000)

flatten = function(filename, output_path = '/data_files/rds_files'){
  dat = stream_in(paste0('data_files/',filename))
  setkey(dat,ts_sec,ts_usec)
  tmp = dat[ , .(ts_sec = ts_sec,
                 ts_usec = ts_usec,
                 pgn = decomp_id(id,'pgn'),
                 dat0 = data.data.0,
                 dat1 = data.data.1,
                 dat2 = data.data.2,
                 dat3 = data.data.3,
                 dat4 = data.data.4,
                 dat5 = data.data.5,
                 dat6 = data.data.6,
                 dat7 = data.data.7),
             .(rownames(dat))]
  saveRDS(tmp, paste0(output_path, '/', strsplit(filename,"\\.")[[1]][1], '.rds'))
}

for (f in list.files('data_files')){
  flatten(f,'data_files/rds_files')
}

################
################

getFastPacketData = function(msg_dt){
  ## validate msg_dt: dat0 is consecutive?
  packets = nrow(msg_dt)
  ts_sec = msg_dt$ts_sec[1]
  ts_usec = msg_dt$ts_usec[1]
  pgn = msg_dt$pgn[1]
  bytes = msg_dt[1,dat1]
  
  data_vect = as.vector(t(msg_dt[ ,.(dat1,dat2,dat3,dat4,dat5,dat6,dat7)]))[-1][1:bytes] 
  
  return(list(pgn = pgn,
              ts_sec = ts_sec,
              ts_usec = ts_usec,
              data_vect = data_vect))
}


signedFromHex = function(hx = hexnum){
  bin_vect = hex2bin(hx)
  if(bin_vect[1]){ ## number is negative
    comp = tail(as.integer(!bin_vect),-1)
    abs_value = as.double(mpfr(paste(comp,collapse ="", sep = ""), base = 2)) + 1
    value = -1 * abs_value
  } else {
    value = as.double(mpfr(paste(bin_vect,collapse ="", sep = ""), base = 2))
  }
  return(value)
}

getValueFromBytes = function(field_id, bv = data_list$data_vect, fields = as.data.table(dict$Fields)){
  signed = fields[Id == field_id, Signed]
  bytes = tail(bv, -fields[Id == field_id,BitOffset/8])[1:fields[Id == field_id,BitLength/8]]
  hexnum = paste(rev(DecToHex(bytes)),collapse = "", sep = "")
  if(signed == T) {
    value = signedFromHex(hexnum)
  } else {
    value = as.double(mpfr(hexnum,base = 16))
  }
  res = fields[Id == field_id, as.numeric(Resolution)]
  return(value * res)
}
################

pgns = as.data.table(fromJSON('pgn.json')$PGNs)

# pgns not in dictionary
# 127252 Heave  
# 65305 unknown
# 130860 unknown
# 130822 unknown

pgns_to_parse = read.csv(text = "pgn,id
                                127245,rudder
                                127250,vesselHeading
                                127251,rateOfTurn
                                127257,attitude
                                127258,magneticVariation
                                128259,speed
                                129029,gnssPositionData,
                                130306,windData,
                                130824,bGWindData")

################
gps_parser = function(dt, dict = pgns[PGN == 129029 & Id == "gnssPositionData"]){
  
  ### safety filtering
  dt = copy(dt[pgn == 129029])
  
  ### this is a dirty hack which loses data
  ### need to actually iterate through, looking for the start of a message and then take the rows subsequent, rather than trying to group them
  dt[ , msg_block_time := round(ts_sec + (ts_usec * 1e-6),1) ] ## may not be appropriate for higher hz pgns
  
  time_block_rows = dt[ , .(n=nrow(dt[msg_block_time == m])),
                        .(m = msg_block_time)]
  
  dt = dt[ msg_block_time %in% time_block_rows[n == 7,m]]
  
  data_list = getFastPacketData(dt[msg_block_time==dt$msg_block_time[1]])
  output = data.table( pgn = data_list$pgn,
                       ts_sec = data_list$ts_sec,
                       ts_usec = data_list$ts_usec,
                       date_value = getValueFromBytes('date',bv = data_list$data_vect, fields = as.data.table(dict$Fields)),
                       time_value = getValueFromBytes('time',bv = data_list$data_vect, fields = as.data.table(dict$Fields)),
                       latitude = getValueFromBytes('latitude',bv = data_list$data_vect, fields = as.data.table(dict$Fields)),
                       longitude = getValueFromBytes('longitude',bv = data_list$data_vect, fields = as.data.table(dict$Fields)))
  
  for(m in 2:length(unique(dt$msg_block_time))){
          data_list = getFastPacketData(dt[msg_block_time==unique(msg_block_time)[m]])
          tmp = data.table(pgn = data_list$pgn,
                           ts_sec = data_list$ts_sec,
                           ts_usec = data_list$ts_usec,
                           date_value = getValueFromBytes('date',bv = data_list$data_vect, fields = as.data.table(dict$Fields)),
                           time_value = getValueFromBytes('time',bv = data_list$data_vect, fields = as.data.table(dict$Fields)),
                           latitude = getValueFromBytes('latitude',bv = data_list$data_vect, fields = as.data.table(dict$Fields)),
                           longitude = getValueFromBytes('longitude',bv = data_list$data_vect, fields = as.data.table(dict$Fields)) )
          
          output = rbind(output,tmp) }
  
  output[ , date_time := as.POSIXct(time_value,
                                    origin = as.Date(date_value,
                                                     origin = '1970-01-01'))]
  return(output)
}

for (f in list.files('data_files/rds_files')){
  dat = readRDS(paste('data_files/rds_files/',f,sep = ""))
  dat = data.table(apply(dat, 2, as.integer))
  tmp = gps_parser(dat)
  
  
  if(!exists("output")){
    output = gps_parser(dat)
  } else {
    output = rbind(output, gps_parser(dat))
  }
}


output = readRDS('data_files/parsed_files/gps.rds')


bob = output[date_time >= '2019-10-25' & date_time < '2019-10-27' & 
               longitude %between% c(174,175) & 
               latitude %between% c(-37,-35)]
 
bob = bob[seq(from = 1,by = 120,length = floor(nrow(bob)/120))]

m <- leaflet(as.data.frame(bob)) %>%
  addTiles() %>%  # Add default OpenStreetMap map tiles
  addPolylines(lng = ~longitude, lat = ~latitude)
  addPopups(lng = bob[which(bob$speed_knots == max(bob$speed_knots)),longitude],
            lat = bob[which(bob$speed_knots == max(bob$speed_knots)),latitude])
m  # Print the map

#################


speed_parser = function(dt, dict = pgns[PGN == 128259 & Id == "speed"]){
  
  ### safety filtering
  dt = copy(dt[pgn == 128259])
  
  dt[, 
     speed := getValueFromBytes(field_id = 'speedWaterReferenced',
                       bv = c(dat0,dat1,dat2,dat3,dat4,dat5,dat6,dat7), 
                       fields = as.data.table(dict$Fields)),
     rownames][ , speed_knots := speed * 1.94]
    
  return(dt[ ,.(pgn,ts_sec,ts_usec,speed,speed_knots)])
}

for (f in list.files('data_files/rds_files')){
  dat = readRDS(paste('data_files/rds_files/',f,sep = ""))
  dat = data.table(apply(dat, 2, as.integer))
  
  if(!exists("output")){
    output = speed_parser(dat)
  } else {
    output = rbind(output, speed_parser(dat))
  }
}

####################
#Investigating Wind

rm(bay_dat)
for(f in list.files('data_files/wind_check')){
  if(!exists("bay_dat")) {
    bay_dat = readRDS(paste('data_files/wind_check/',f, sep = ""))
  } else {
    bay_dat = rbind(bay_dat,
                    readRDS(paste('data_files/wind_check/',f, sep = "")))
  }
}

bay_gps = gps_parser(bay_dat)

m <- leaflet(as.data.frame(bay_gps)) %>%
  addTiles() %>%  # Add default OpenStreetMap map tiles
  addPolylines(lng = ~longitude, lat = ~latitude)
m  # Print the map


### wind_parser = function(dt, dict = pgns[PGN == 130306 & Id == "windData"]){
  
  ### wind data
dict = pgns[PGN == 130306 & Id == "windData"]
dt = copy(bay_dat[pgn == 130306])

dt[,
   `:=`(windSpeed = getValueFromBytes(field_id = 'windSpeed',
                                      bv = c(dat0,dat1,dat2,dat3,dat4,dat5,dat6,dat7),
                                      fields = as.data.table(dict$Fields)),
        windAngle = getValueFromBytes(field_id = 'windAngle',
                                      bv = c(dat0,dat1,dat2,dat3,dat4,dat5,dat6,dat7), 
                                      fields = as.data.table(dict$Fields))) ,
   by = seq_len(NROW(dt))][ , 
              windAngle := {tmp = windAngle * (180/pi)
                            if(tmp > 180){ 
                              tmp - 360 
                              } else { 
                              tmp } },by = seq_len(NROW(dt))]

bay_wind = dt[windSpeed < 20, .(ts_sec,ts_usec,pgn,windSpeed,windAngle)]

setkey(bay_gps,ts_sec,ts_usec)
setkey(bay_wind, ts_sec,ts_usec)
bay = merge(bay_gps,
            bay_wind,
            by = c('ts_sec','ts_usec','pgn'),
            all = T)

bay[ , ts := ts_sec + ts_usec * 0.000001] 


###################################
bay = readRDS('data_files/bay_dat/bay.rds')

bay$lat_interp = approx(x = bay[!is.na(latitude),ts],
                        y = bay[!is.na(latitude),latitude],
                        xout = bay$ts)$y

bay$lon_interp = approx(x = bay[!is.na(longitude),ts],
                        y = bay[!is.na(longitude),longitude],
                        xout = bay$ts)$y

windSpeedPal = colorNumeric(palette = 'Blues',domain = range(bay[pgn == 130306,windSpeed]))

portPal = colorNumeric(palette = c('Reds'),
                       domain = c(1,180))
stbPal = colorNumeric(palette = c('Greens'),
                      domain = c(1,180))
windAnglePal = function(angles){
  tmp = sapply(angles,
               function(x){
                 ifelse(sign(x) == 1,
                        stbPal(x),
                        portPal(-x))
               })
  return(tmp)
}

m <- leaflet(as.data.frame(bay[pgn == 130306][seq(from = 1,
                                                  to = nrow(bay[pgn == 130306]),
                                                  by = 500)])) %>%
  addTiles() %>%  # Add default OpenStreetMap map tiles
  addCircleMarkers(lng = ~lon_interp, 
                   lat = ~lat_interp, 
                   color = ~windAnglePal(windAngle),
                   popup = ~htmlEscape(ts),
                   radius = 1)
m  # Print the map

#####################
bay = readRDS('data_files/bay_dat/bay.rds')

dict = pgns[PGN == 127257 & Id == "attitude"]
dt = copy(bay_dat[pgn == 127257])

dt[seq(from = 1, to = nrow(dt), by = 1000),
   `:=`(
        pitch = getValueFromBytes(field_id = 'pitch',
                                      bv = c(dat0,dat1,dat2,dat3,dat4,dat5,dat6,dat7), 
                                      fields = as.data.table(dict$Fields)) * (180/pi),
        roll = getValueFromBytes(field_id = 'roll',
                                  bv = c(dat0,dat1,dat2,dat3,dat4,dat5,dat6,dat7), 
                                  fields = as.data.table(dict$Fields)) * (180/pi)
        ) ,
   by = seq(from = 1, to = nrow(dt), by = 100)]

bob = merge(bay,dt[,.(ts_sec,
                      ts_usec,
                      ts,
                      pgn,
                      pitch,roll)], 
            by = c('ts_sec','ts_usec','pgn','ts'),
            all = T)


bob$lat_interp = approx(x = bob[!is.na(latitude),ts],
                        y = bob[!is.na(latitude),latitude],
                        xout = bob$ts)$y

bob$lon_interp = approx(x = bob[!is.na(longitude),ts],
                        y = bob[!is.na(longitude),longitude],
                        xout = bob$ts)$y

m <- leaflet(as.data.frame(bob)) %>%
  addTiles() %>%  # Add default OpenStreetMap map tiles
  addCircleMarkers(lng = ~lon_interp, 
                   lat = ~lat_interp, 
                   popup = ~htmlEscape(roll),
                   radius = 1)
m  # Print the map

