
# Import vehicle registry data for 2012

registry.wide <- read.csv("personbilaritrafik.csv", header=TRUE)

# produce long file with total fleet
registry.tot <- registry.wide %>%
  dplyr::select(Year, Komkod, Kommun, Bensin, Diesel, El, 
                Etanol.hybrid, Bensin.El, Gas, Övriga, Totalt, Miljöbil, ee.index, rr.index) %>%
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
                                   AFV = c("Miljöbil"))

# Get share of clean vehicles pre-2008 for all-county
share.clean.t08 <- weighted.mean(x=registry$t08.pv[registry$Drivmedel=="AFV"], 
                                 w=registry$tot.veh[registry$Drivmedel=="AFV"])
share.clean.f09 <- weighted.mean(x=registry$f09.pv[registry$Drivmedel=="AFV"], 
                                 w=registry$tot.veh[registry$Drivmedel=="AFV"])


