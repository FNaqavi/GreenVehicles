# Load and organize data files

setwd("C:/Users/joelp/OneDrive - KTH/Data/Passages")

library(tidyverse, magrittr)

# Import text files
pass.control.12 <- read.csv("KTH_KontrollGruppPassager_2012.txt", header=TRUE)
pass.control.13 <- read.csv("KTH_KontrollGruppPassager_2013.txt", header=TRUE)
pass.treat.12 <- read.csv("KTH_BehandlingsGruppPassager_2012.txt", header=TRUE)
pass.treat.13 <- read.csv("KTH_BehandlingsGruppPassager_2013.txt", header=TRUE)

# Create year variable
pass.control.12$year <- 2012
pass.control.13$year <- 2013
pass.treat.12$year <- 2012
pass.treat.13$year <- 2013

# Create experimental group variable
pass.control.12$expgrp <- "control"
pass.control.13$expgrp <- "control"
pass.treat.12$expgrp <- "treat"
pass.treat.13$expgrp <- "treat"

# Merge datasets
passages <- rbind(pass.control.12, pass.control.13, pass.treat.12, pass.treat.13)
passages$expgrp <- as.factor(passages$expgrp)

# Create unified fuel variable
passages$Drivmedel <- passages$Drivmedel.1
passages$Drivmedel <- paste(passages$Drivmedel.1, passages$Drivmedel.2, sep=".")
passages$Drivmedel <- as.factor(passages$Drivmedel)
passages$Drivmedel <- fct_collapse(passages$Drivmedel,
                                   Petrol = c("Bensin.Okänd"),
                                   Diesel = c("Diesel.Okänd"),
                                   Electric = c("El.Okänd"),
                                   Electric.Hybrid = c("Bensin.El"),
                                   Ethanol = c("Etanol.Okänd","Bensin.Etanol"),
                                   Natural.Gas = c("Bensin.Metangas","Metangas.Metangas","Metangas.Okänd"),
                                   Other = c(".","Motorgas.Okänd"))
passages$Miljöbil[passages$Drivmedel %in% c("Electric","Electric.Hybrid","Ethanol","Natural.Gas","Other")] <- TRUE
passages$Miljöbil[passages$Drivmedel %in% c("Petrol","Diesel")] <- FALSE
passages$FuelCat[passages$Drivmedel %in% c("Electric","Electric.Hybrid","Ethanol","Natural.Gas","Other")] <- "AFV"
passages$FuelCat[passages$Drivmedel %in% c("Petrol","Diesel")] <- "CV"

# Add municipalities to Passages based on localities

passages$Ort <- passages$Ägare.ort
levels(passages$Ort) <- trimws(levels(passages$Ort), which="right")
localities <- read.csv("Localities.csv", header=TRUE)
levels(localities$Ort) <- toupper(levels(localities$Ort))
levels(localities$Kommun) <- toupper(levels(localities$Kommun))

passages <- passages %>%
  left_join(localities, by="Ort")

# Import vehicle registry data for 2012

registry.wide <- read.csv("personbilaritrafik.csv", header=TRUE)

# produce long file with total fleet
registry.tot <- registry.wide %>%
  dplyr::select(Year, Komkod, Kommun, Bensin, Diesel, El, 
         Etanol.hybrid, Bensin.El, Gas, Övriga, Totalt, Miljöbil) %>%
  gather(c("Bensin", "Diesel", "El", "Etanol.hybrid", 
           "Bensin.El","Gas","Övriga","Totalt", "Miljöbil"), 
         key="Drivmedel", value="tot.veh", na.rm=TRUE)
# produce long file with fleet subset from 2009 onward
registry.f09 <- registry.wide %>%
  dplyr::select(Year, Komkod, Kommun, Bensin.from09, Diesel.from09, El.from09, 
         Etanol.hybrid.from09, Bensin.El.from09, Gas.from09, Övriga.from09, Totalt.from09, Miljöbil.from09) %>%
  gather(c("Bensin.from09", "Diesel.from09", "El.from09", "Etanol.hybrid.from09", 
           "Bensin.El.from09","Gas.from09","Övriga.from09","Totalt.from09", "Miljöbil.from09"), 
         key="Drivmedel", value="f09.veh", na.rm=TRUE)
# rename fuel types
registry.f09$Drivmedel <- sub(pattern=".from09", replacement="",
                              x=registry.f09$Drivmedel)
# merge
registry <- registry.tot %>%
  left_join(registry.f09, by=c("Year","Komkod","Kommun","Drivmedel"))
#registry$f09.veh[is.na(registry$f09.veh)] <- 0
registry$f09.pv <- registry$f09.veh/registry$tot.veh
registry$t08.pv <- (registry$tot.veh-registry$f09.veh)/registry$tot.veh

#Modify Drivmedel in "registry" to conform to "passages"
registry$Drivmedel <- as.factor(registry$Drivmedel)
registry$Drivmedel <- fct_collapse(registry$Drivmedel,
                                   Petrol = c("Bensin"),
                                   Diesel = c("Diesel"),
                                   Electric = c("El"),
                                   Electric.Hybrid = c("Bensin.El"),
                                   Ethanol = c("Etanol.hybrid"),
                                   Natural.Gas = c("Gas"),
                                   Other = c("Övriga"),
                                   Total = c("Totalt"),
                                   CleanCar = c("Miljöbil"))

# Get share of clean vehicles pre-2008 for all-county
share.clean.t08 <- weighted.mean(x=registry$t08.pv[registry$Drivmedel=="CleanCar"], 
                                 w=registry$tot.veh[registry$Drivmedel=="CleanCar"])
share.clean.f09 <- weighted.mean(x=registry$f09.pv[registry$Drivmedel=="CleanCar"], 
                                 w=registry$tot.veh[registry$Drivmedel=="CleanCar"])

