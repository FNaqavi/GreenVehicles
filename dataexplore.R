# needed for the align.time function
#install.packages("xts")
library(xts)
library(ggplot2)
library(lubridate)

passages$Passagetid[hour(hms(passages$Passagetid)) > 19] <- NA # remove data where the passage is after 19.00
passages$tid <- strptime(paste(passages$Passagedatum,passages$Passagetid),format="%Y-%m-%d %H:%M:%S")
levels(passages$Passagedatum) # check what dates; 9 days 2012, 9 days 2013

passages$tid.round <- align.time(passages$tid,n=10*60) # round time stamps to nearest 10-minute period; can be changed later as needed
passages$date <- as.Date(passages$tid.round) # extracts dates only
passages$clock <- format(passages$tid.round,"%H:%M:%S") # extracts times only; note that this returns character, not "time" data type (POSIXct)
passages$tod.period <- hms(format(passages$tid,"%H:%M:%S")) # extracts times only in period format
passages$tod <- ymd(20120523)+passages$tod.period # uses time-arithmatic to create pseudodate 


levels(as.factor(passages$clock)) # check what times; there are some observations > 21:00 that seems wrong

# Passages histogram by time-of-day, for each year
no.pass.year <- table(clock,passages$year) # tabulates passages by time period, for each year separately
x.vec <- as.POSIXct(row.names((no.pass.year)),format="%H:%M:%S") # formats time-of-day for the x-axis
plot(x.vec,no.pass.year[,1],type="l")
lines(x.vec,no.pass.year[,2],type="l",col="red")

# Passage-time density plots for 2012 and 2013, split by exemption
ggplot(subset(passages, Ny.ägare.mellan.period.1.och.2="Nej"), 
       aes(x = tod, color = as.factor(exempt12))) +
  geom_density() +
  facet_grid(year ~ .)

