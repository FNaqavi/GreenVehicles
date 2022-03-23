# Reallocate some passages' cars to control group
# Be sure run ImportPassages first, and either run ImportRegistry or set "share.clean.f09".

setwd("C:/Users/naqavi/OneDrive - KTH/!Joel/Passages/GreenVehicles")

library(tidyverse, magrittr, lubridate)

# Compute nominal charges
passages$DoW <- as.factor(weekdays(as.Date(passages$Passagedatum)))
passages <- passages %>% 
  mutate(PassageDT = lubridate::ymd_hms(paste0(passages$Passagedatum, " ", passages$Passagetid)))
passages <- passages %>%
  mutate(PassageTime = lubridate::hms(passages$Passagetid))
passages$price <- 0
passages$price[passages$PassageTime >= lubridate::hms("06:30:00") & passages$PassageTime < lubridate::hms("07:00:00")] <- 10
passages$price[passages$PassageTime >= lubridate::hms("07:00:00") & passages$PassageTime < lubridate::hms("07:30:00")] <- 15
passages$price[passages$PassageTime >= lubridate::hms("07:30:00") & passages$PassageTime < lubridate::hms("08:30:00")] <- 20
passages$price[passages$PassageTime >= lubridate::hms("08:30:00") & passages$PassageTime < lubridate::hms("09:00:00")] <- 15
passages$price[passages$PassageTime >= lubridate::hms("09:00:00") & passages$PassageTime < lubridate::hms("15:30:00")] <- 10
passages$price[passages$PassageTime >= lubridate::hms("15:30:00") & passages$PassageTime < lubridate::hms("16:00:00")] <- 15
passages$price[passages$PassageTime >= lubridate::hms("16:00:00") & passages$PassageTime < lubridate::hms("17:30:00")] <- 20
passages$price[passages$PassageTime >= lubridate::hms("17:30:00") & passages$PassageTime < lubridate::hms("18:00:00")] <- 15
passages$price[passages$PassageTime >= lubridate::hms("18:00:00") & passages$PassageTime < lubridate::hms("18:30:00")] <- 10
passages$PassageTime <- NULL

# Since 2013 observations only seem to exist during charging periods, filter out 
# the same for 2012.
passages <- passages %>%
  filter(passages$price > 0)

# Extract vehicle-specific information 
vehicles <- passages %>%
  group_by(AnonymRegno) %>%
  summarize(Juridisk.eller.fysisk = first(Juridisk.eller.fysisk),
            Ny.ägare.mellan.period.1.och.2 = first(Ny.ägare.mellan.period.1.och.2),
            Drivmedel.1 = first(Drivmedel.1),
            Drivmedel.2 = first(Drivmedel.2),
            C02.Driv.1 = first(C02.Driv.1),
            C02.Driv.2 = first(C02.Driv.2),
            Ägare.postnr = first(Ägare.postnr),
            Ägare.ort = first(Ägare.ort),
            Drivmedel = first(Drivmedel),
            FuelCat = first(FuelCat),
            Ort = first(Ort),
            Kommun = first(Kommun),
            expgrp = first(expgrp))

# Also create the first long vehicles table (separate rows for each Year)
veh.year.12 <- vehicles %>%
  mutate(Year=2012)
veh.year.13 <- vehicles %>%
  mutate(Year=2013)
veh.year <- rbind(veh.year.12, veh.year.13)

# relabel experimental group variable
levels(vehicles$expgrp) <- c("Paying in 2012","Exempt in 2012")
levels(veh.year$expgrp) <- c("Paying in 2012","Exempt in 2012")

# Aggregate passages to unique vehicles
pass.trips.2012 <- passages %>%
  dplyr::filter(Year == 2012) %>%
  group_by(AnonymRegno) %>%
  summarize(totalprice.12 = sum(price))
pass.trips.2013 <- passages %>%
  dplyr::filter(Year == 2013) %>%
  group_by(AnonymRegno) %>%
  summarize(totalprice.13 = sum(price))
#Alternatively,...
pass.trips <- passages %>%
  group_by(AnonymRegno, Year) %>%
  summarize(totalprice = sum(price))

# Merge back into vehicles
vehicles <- vehicles %>%
  full_join(pass.trips.2012, by="AnonymRegno")
vehicles <- vehicles %>%
  full_join(pass.trips.2013, by="AnonymRegno")
# Alternatively,
veh.year <- veh.year %>%
  full_join(pass.trips, by=c("AnonymRegno","Year"))

# Set NAs in total price to zero
vehicles$totalprice.12[is.na(vehicles$totalprice.12)] <- 0
vehicles$totalprice.13[is.na(vehicles$totalprice.13)] <- 0
veh.year$totalprice[is.na(veh.year$totalprice)] <- 0


# Filter out vehicles that are suspect, put OK data in new df
pass.veh <- vehicles %>%
  dplyr::filter(!is.na(vehicles$totalprice.12) & # no observed trips in 2012
                  !is.na(vehicles$totalprice.13) & # no observed trips in 2013
                  vehicles$Ny.ägare.mellan.period.1.och.2=="Nej" & # not same owner in 2012 and 2013
                  vehicles$Juridisk.eller.fysisk=="F" & # not privately owned
                  !is.na(vehicles$Kommun)) # not registered within Stockholm County
# Same for long table
veh.year <- veh.year %>%
  dplyr::filter(!is.na(veh.year$totalprice) &
                  veh.year$Ny.ägare.mellan.period.1.och.2=="Nej" &
                  veh.year$Juridisk.eller.fysisk=="F" &
                  !is.na(veh.year$Kommun))


# Compute change in nominal price
pass.veh$totalprice.diff <- pass.veh$totalprice.13 - pass.veh$totalprice.12

# Do some density plots

# Use a common bandwidth adjustment
bw.adjust <- 2

# Nominal price for 2012/2013, using long table
ggplot(veh.year, aes(totalprice, fill=expgrp)) +
  geom_density(alpha=0.5, adjust=bw.adjust) +
  xlim(0,600) +
  theme(legend.position="top") +
  facet_wrap( ~ Year, ncol=2) +
  labs(fill="Group", 
       x="Total Nominal Price of Crossings",
       y = "Density")


# Estimate a density function for each group
epdf.pricediff.control <- density(pass.veh$totalprice.diff[pass.veh$FuelCat=="CV"], adjust=bw.adjust)
epdf.pricediff.mixed <- density(pass.veh$totalprice.diff[pass.veh$FuelCat=="AFV"], adjust=bw.adjust)

# create a density function from the control group's PDF
densfun.control <- approxfun(epdf.pricediff.control$x, epdf.pricediff.control$y)

# get densities for the treatment group's data points
pass.veh$pr.nex <- 0
pass.veh$pr.nex[pass.veh$FuelCat=="AFV"] <- 
  densfun.control(pass.veh$totalprice.diff[pass.veh$FuelCat=="AFV"])
pass.veh <- pass.veh[!is.na(pass.veh$pr.nex),]
pass.veh$pr.nex[pass.veh$FuelCat=="AFV"] <- pass.veh$pr.nex[pass.veh$FuelCat=="AFV"]/
  sum(pass.veh$pr.nex[pass.veh$FuelCat=="AFV"])

# take samples from the treatment group and reassign them to control
n.sample <- share.clean.f09*dim(pass.veh[pass.veh$FuelCat=="AFV",])[1]
set.seed(5)
sampled.reg <- sample(pass.veh$AnonymRegno[pass.veh$FuelCat=="AFV"], size=n.sample, 
                      replace=FALSE, prob=pass.veh$pr.nex[pass.veh$FuelCat=="AFV"])
# reset all FuelCats to treatment
pass.veh$expgrp[pass.veh$FuelCat=="AFV"] <- "Exempt in 2012" 
veh.year$expgrp[veh.year$FuelCat=="AFV"] <- "Exempt in 2012" 
# now change the sampled FuelCats to control
pass.veh$expgrp[pass.veh$AnonymRegno %in% sampled.reg] <- "Paying in 2012" 
veh.year$expgrp[veh.year$AnonymRegno %in% sampled.reg] <- "Paying in 2012"

# Do some density plots and stats using the synthetic control group

# Use a common bandwidth adjustment
bw.adjust <- 1.5

# 2012 and 2013 nominal price

plot.to.file = FALSE
if(plot.to.file) {svg("tnomprice.byyear.svg", width=7, height=3.5)}
ggplot(veh.year, aes(totalprice, fill=FuelCat)) +
  geom_density(alpha=0.5, adjust=bw.adjust) +
  xlim(0,600) +
  theme(legend.position="top") +
  facet_wrap( ~ Year, ncol=2) +
  labs(fill="Group", 
       x="Total Nominal Price of Crossings",
       y = "Density")
if(plot.to.file) {dev.off()}

t.test(totalprice.12 ~ expgrp, data=pass.veh)
t.test(totalprice.13 ~ expgrp, data=pass.veh)

# Change in total nominal price - before reclass
plot.to.file = FALSE
if(plot.to.file) {svg("dnomprice.preadjust.svg", width=3.5, height=3.5)}
ggplot(pass.veh, aes(totalprice.diff, fill=FuelCat)) +
  geom_density(alpha=0.5, adjust=bw.adjust) +
  xlim(-400,400) +
  theme(legend.position="top") +
  labs(fill="Car Type", 
       x="Change in Total Nominal Price of Crossings",
       y = "Density")
if(plot.to.file) {dev.off()}

# Change in total nominal price - after reclass
plot.to.file = FALSE
if(plot.to.file) {svg("dnomprice.postadjust.svg", width=3.5, height=3.5)}
ggplot(pass.veh, aes(totalprice.diff, fill=expgrp)) +
  geom_density(alpha=0.5, adjust=bw.adjust) +
  xlim(-400,400) +
  theme(legend.position="top") +
  labs(fill="Group", 
       x="Change in Total Nominal Price of Crossings",
       y = "Density")
if(plot.to.file) {dev.off()}
t.test(totalprice.diff ~ expgrp, data=pass.veh)

# Update expgrp in passages data.table

passages$expgrp.old <- NULL
passages <- passages %>%
  left_join(dplyr::select(pass.veh, "AnonymRegno", "expgrp"), by="AnonymRegno")
colnames(passages)[colnames(passages)=="expgrp.x"] <- "expgrp.old"
colnames(passages)[colnames(passages)=="expgrp.y"] <- "expgrp"

