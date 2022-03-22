# Compute comparison statistics for before-after exemption expires: 
# Num. days crossing, Num. crossings per crossing-day, and Time of crossing
# Be sure to run FindExempt first!

library(tidyverse, magrittr, lubridate)

# Aggregate by day and Year to summarize averages
veh.daystats <- passages %>%
  dplyr::select(AnonymRegno, Year, Passagedatum, price) %>%
  group_by(AnonymRegno, Year, Passagedatum) %>%
  summarize(avg.price = mean(price), day.pass=n())

veh.yearstats <- veh.daystats %>%
  dplyr::select(AnonymRegno, Year, avg.price, day.pass) %>%
  group_by(AnonymRegno, Year) %>%
  summarize(avg.days = n(), avg.day.pass = mean(day.pass), avg.price = mean(avg.price))

# Merge back into vehicles

pass.veh <- pass.veh %>%
  left_join(veh.yearstats[veh.yearstats$Year==2012,], by="AnonymRegno", suffix=c("",".12")) %>%
  left_join(veh.yearstats[veh.yearstats$Year==2013,], by="AnonymRegno", suffix=c("",".13"))
colnames(pass.veh)[colnames(pass.veh)=="avg.days"] <- "avg.days.12"
colnames(pass.veh)[colnames(pass.veh)=="avg.day.pass"] <- "avg.day.pass.12"
colnames(pass.veh)[colnames(pass.veh)=="avg.price"] <- "avg.price.12"
pass.veh <- pass.veh %>%
  mutate(avg.days.diff = avg.days.13 - avg.days.12,
         avg.day.pass.diff = avg.day.pass.13 - avg.day.pass.12,
         avg.price.diff = avg.price.13 - avg.price.12)

# Or, merge into long version 
veh.year <- veh.year %>%
  left_join(veh.yearstats, by=c("AnonymRegno","Year"))

# Also code variables for whether any passage was detected
pass.veh$any.pass.12 <- 0
pass.veh$any.pass.12[!is.na(pass.veh$avg.days.12)] <- 1
pass.veh$any.pass.13 <- 0
pass.veh$any.pass.13[!is.na(pass.veh$avg.days.13)] <- 1
pass.veh$any.pass.diff <- pass.veh$any.pass.13 - pass.veh$any.pass.12
veh.year$any.pass <- 0
veh.year$any.pass[!is.na(veh.year$avg.days)] <- 1


# Do some t-tests
t.any.12 <- t.test(any.pass.12 ~ expgrp, data=pass.veh)
t.any.13 <- t.test(any.pass.13 ~ expgrp, data=pass.veh)
t.any.d <- t.test(any.pass.diff ~ expgrp, data=pass.veh)

t.days.12 <- t.test(avg.days.12 ~ expgrp, data=pass.veh)
t.days.13 <- t.test(avg.days.13 ~ expgrp, data=pass.veh)
t.days.d <- t.test(avg.days.diff ~ expgrp, data=pass.veh)

t.pass.12 <- t.test(avg.day.pass.12 ~ expgrp, data=pass.veh)
t.pass.13 <- t.test(avg.day.pass.13 ~ expgrp, data=pass.veh)
t.pass.d <- t.test(avg.day.pass.diff ~ expgrp, data=pass.veh)

t.price.12 <- t.test(avg.price.12 ~ expgrp, data=pass.veh)
t.price.13 <- t.test(avg.price.13 ~ expgrp, data=pass.veh)
t.price.d <- t.test(avg.price.diff ~ expgrp, data=pass.veh)

# Make some plots

# Detected at all, 2012 and 2013
table(pass.veh$any.pass.12[pass.veh$expgrp=="Paying in 2012"])/
  sum(table(pass.veh$any.pass.12[pass.veh$expgrp=="Paying in 2012"]))
table(pass.veh$any.pass.13[pass.veh$expgrp=="Paying in 2012"])/
  sum(table(pass.veh$any.pass.13[pass.veh$expgrp=="Paying in 2012"]))
table(pass.veh$any.pass.12[pass.veh$expgrp=="Exempt in 2012"])/
  sum(table(pass.veh$any.pass.12[pass.veh$expgrp=="Exempt in 2012"]))
table(pass.veh$any.pass.13[pass.veh$expgrp=="Exempt in 2012"])/
  sum(table(pass.veh$any.pass.13[pass.veh$expgrp=="Exempt in 2012"]))

# # Days as histogram: 2012 & 2013
# diff
if(plot.to.file) {svg("hist.avg.days.diff.svg", width=3.5, height=3.5)}
ggplot(pass.veh, aes(x=avg.days.diff, fill=expgrp)) +
  geom_density(adjust=bw.adjust, alpha=.5) +
  theme(legend.position="top") +
  labs(fill="Group", 
       x="Change in # Crossing Days (of 10 Weekdays)",
       y = "Density")
if(plot.to.file) {dev.off()}

# Or, using long file

plot.to.file = TRUE
if(plot.to.file) {svg("hist.avg.days.byyear.svg", width=7, height=3.5)}
ggplot(veh.year, aes(x=avg.days, fill=expgrp)) +
  geom_histogram(binwidth=1, alpha=.5, position="identity") +
  xlim(0,10) +
  theme(legend.position="top") +
  facet_grid(.~Year) +
  labs(fill="Group", 
       x="# Crossing Days (of 10 Weekdays)",
       y = "Count")
if(plot.to.file) {dev.off()}



# Avg. Crossings per day
bw.adjust <- 2
# Change
ggplot(pass.veh, aes(avg.day.pass.diff, fill=expgrp)) +
  geom_density(alpha=0.5, adjust=bw.adjust) +
  xlim(-5,5) +
  theme(legend.position="top") +
  labs(fill = "Group", 
       x = "Change in Avg. # Crossings/Day",
       y = "#Density")

# 2012 vs 2013
plot.to.file = TRUE
if(plot.to.file) {svg("hist.avg.day.pass.byyear.svg", width=7, height=3.5)}
ggplot(veh.year, aes(x=avg.day.pass, fill=expgrp)) +
  geom_histogram(binwidth=1, alpha=.5, position="identity") +
  xlim(0,8) +
  theme(legend.position="top") +
  facet_grid(.~Year) +
  labs(fill="Group", 
       x="Avg. # of Crossings per Day",
       y = "Count")
if(plot.to.file) {dev.off()}



# Avg. Price per crossing
bw.adjust <- 2
# Change
ggplot(pass.veh, aes(avg.price.diff, fill=expgrp)) +
  geom_density(alpha=0.5, adjust=bw.adjust) +
  theme(legend.position="top") +
  labs(fill = "Group", 
       x = "Change in Avg. Nominal Price per Crossing",
       y = "Density")

# 2012 & 2013 
plot.to.file = TRUE
if(plot.to.file) {svg("hist.avg.price.byyear.svg", width=7, height=3.5)}
bw.adjust = 2
ggplot(veh.year, aes(avg.price, fill=expgrp)) +
  geom_density(alpha=0.5, adjust=bw.adjust) +
  facet_grid(.~Year) +
  theme(legend.position="top") +
  labs(fill="Group", 
       x="Avg. Nominal Price per Crossing",
       y = "Density")
if(plot.to.file) {dev.off()}


