# File for computing proportions of vehicles that should be exempt, 
# based on registry data.

# Aggregate new registrations from earliest data up to june 2012

# First aggregate by year
newreg.byyear <- newreg %>% 
  filter(date <= as.Date("2012-06-01")) %>%
  group_by(year, kommun, drivmedel) %>%
  summarize(n.reg.y=sum(n.reg), na.rm=TRUE)

# Then, by all years
newreg.until1206 <- newreg.byyear %>%
  group_by(kommun, drivmedel) %>%
  summarize(n.reg.t=sum(n.reg.y), na.rm=TRUE)

# Now, by all fuel types
newreg.until1206.af <- newreg.until1206 %>%
  group_by(kommun) %>%
  summarize(n.reg.t.f = sum(n.reg.t))

# Finally, for all munis
newreg.until1206.af.sst <- newreg.until1206.af %>%
  summarize(n.reg.t.f.s = sum(n.reg.t.f))

# Now attach to vehicle registry data

