# Load and organize data files

setwd("C:/Users/naqavi/OneDrive - KTH/!Joel/Passages")

library(tidyverse)
library(dplyr)
library(magrittr)
library(forcats)

# Import text files
pass.control.12 <- read.csv("KTH_KontrollGruppPassager_2012.txt", header=TRUE)
pass.control.13 <- read.csv("KTH_KontrollGruppPassager_2013.txt", header=TRUE)
pass.treat.12 <- read.csv("KTH_BehandlingsGruppPassager_2012.txt", header=TRUE)
pass.treat.13 <- read.csv("KTH_BehandlingsGruppPassager_2013.txt", header=TRUE)

# Create Year variable
pass.control.12$Year <- 2012
pass.control.13$Year <- 2013
pass.treat.12$Year <- 2012
pass.treat.13$Year <- 2013

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
passages$FuelCat[passages$Drivmedel %in% c("Electric","Electric.Hybrid","Ethanol","Natural.Gas","Other")] <- "AFV"
passages$FuelCat[passages$Drivmedel %in% c("Petrol","Diesel")] <- "CV"

# Add municipalities to Passages based on localities

passages$Ort <- passages$Ägare.ort
passages$Ort <- trimws(passages$Ort, which="both")
localities <- read.csv("Localities.csv", header=TRUE)
localities$Ort <- toupper(localities$Ort)
localities$Kommun <- toupper(localities$Kommun)

passages <- passages %>%
  left_join(localities, by="Ort")
