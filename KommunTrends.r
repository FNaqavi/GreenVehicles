# Be sure to run ImportPassages, ImportRegistry, FindExempt, and CompareTrips first.

library(MASS)

# Make sure Kommun is a string, for matching purposes later
registry.wide$Kommun <- trimws(as.character(registry.wide$Kommun), which="both")
registry$Kommun <- trimws(as.character(registry$Kommun), which="both")
veh.year$Kommun <- trimws(as.character(veh.year$Kommun), which="both")
pass.veh$Kommun <- trimws(as.character(pass.veh$Kommun), which="both")

# Add Kommun indices to vehicle tables
pass.veh <- pass.veh %>%
  left_join(registry.wide[registry.wide$Year==2012,
                          c("Year","Kommun","ee.index","rr.index")], 
            by="Kommun")
veh.year <- veh.year %>%
  left_join(registry.wide[c("Year","Kommun","ee.index","rr.index")],
            by=c("Year","Kommun"))

# Add incomes by post code and join to vehicle tables
post.incomes <- read.csv("Incomes2009.csv", header=TRUE)
pass.veh <- pass.veh %>%
  left_join(post.incomes[,c("Postnr", "Avg.inc.20.29", "Avg.inc.30.64", 
                            "Med.inc.20.29", "Med.inc.30.64")], 
            by=c("Ägare.postnr"="Postnr"))
veh.year <- veh.year %>%
  left_join(post.incomes[,c("Postnr", "Avg.inc.20.29", "Avg.inc.30.64", 
                            "Med.inc.20.29", "Med.inc.30.64")],
            by=c("Ägare.postnr"="Postnr"))

# Make an income variable in thousands
veh.year$Med.inck.30.64 <- veh.year$Med.inc.30.64/1000
# Make log variables for the continuous indicators
veh.year$ln.totalprice <- log(veh.year$totalprice)
veh.year$ln.avg.price <- log(veh.year$avg.price)
# Make factors as appropriate
veh.year$Year = as.factor(veh.year$Year)

# Make a variable for average (total) nom price /day over the 10 days
veh.year$avgpricep10 <- veh.year$totalprice/10


# Plot behaviors against explanatory variables

# Total nominal price 2012 and 2013 ~ income
ggplot(veh.year, aes(x=Med.inc.30.64, y=avgpricep10, color=expgrp)) +
  geom_point(shape=1) +    
  geom_smooth() +
  ylim(0,150) +
  facet_grid(.~Year) +
  theme(legend.position="top") +
  labs(color="Group", 
       x="Median income of post code",
       y = "Avg. nominal price per day over 10 days (SEK)")

# d Total nominal price ~ income
plot.to.file = TRUE
if(plot.to.file) {svg("dtotalprice.byincome.svg", width=7, height=3.5)}
ggplot(pass.veh, aes(x=Med.inc.30.64, y=totalprice.diff, color=expgrp)) +
  #geom_point(alpha=0.25) +    
  geom_smooth() +
  #ylim(-600,600) +
  geom_hline(yintercept=0) +
  labs(color="Group", 
       x="Median income at home post code, SEK",
       y = "Mean Chg. in Avg. Nominal Price/Day, SEK") +
  scale_x_continuous(labels = scales::comma)
if(plot.to.file) {dev.off()}


# d any detected crossings ~ income
plot.to.file = TRUE
if(plot.to.file) {svg("danypass.byincome.svg", width=7, height=3.5)}
ggplot(pass.veh, aes(x=Med.inc.30.64, y=any.pass.diff, color=expgrp)) +
  geom_smooth() +
  #ylim(-1,1) +
  geom_hline(yintercept=0) +
  labs(color="Group", 
       x="Median income at home post code, SEK",
       y = "Mean Change in Any Detected Passage") +
  scale_x_continuous(labels = scales::comma)
if(plot.to.file) {dev.off()}


# # crossing days 2012 and 2013 ~ income
ggplot(veh.year, aes(x=Med.inc.30.64, y=avg.days, color=expgrp)) +
  geom_point(shape=1) +    
  geom_smooth() +
  facet_grid(.~Year) +
  theme(legend.position="top") +
  labs(color="Group", 
       x="Median income of post code",
       y = "# Days Crossing")
# d # crossing days ~ income
plot.to.file = TRUE
if(plot.to.file) {svg("davgdays.byincome.svg", width=7, height=3.5)}
ggplot(pass.veh, aes(x=Med.inc.30.64, y=avg.days.diff, color=expgrp)) +
  #geom_point(alpha=0.25) +   
  geom_hline(yintercept=0) + 
  geom_smooth() +
  labs(color="Group", 
       x="Median income at home post code, SEK",
       y = "Mean Change in # Days Crossing") +
  scale_x_continuous(labels = scales::comma)
if(plot.to.file) {dev.off()}

# avg # crossings/day 2012 & 2013 ~ income
ggplot(veh.year, aes(x=Med.inc.30.64, y=avg.day.pass, color=expgrp)) +
  geom_point(shape=1) +    
  geom_smooth() +
  facet_grid(.~Year) +
  theme(legend.position="top") +
  labs(color="Group", 
       x="Median income of post code",
       y = "Avg. # Crossings per Day")
# d avg # crossings/day ~ income
plot.to.file = TRUE
if(plot.to.file) {svg("ddaypass.byincome.svg", width=7, height=3.5)}
ggplot(pass.veh, aes(x=Med.inc.30.64, y=avg.day.pass.diff, color=expgrp)) +
  #geom_point(alpha=0.25) +
  #ylim(-6,6) +
  geom_hline(yintercept=0) +
  geom_smooth() +
  labs(color="Group", 
       x="Median income at home post code, SEK",
       y = "Mean Change in Average # Crossings / Day") +
  scale_x_continuous(labels = scales::comma)
if(plot.to.file) {dev.off()}

# avg. price per crossing 2012 & 2013 ~ income
ggplot(veh.year, aes(x=Med.inc.30.64, y=avg.price, color=expgrp)) +
  geom_point(shape=1) +    
  geom_smooth() +
  facet_grid(.~Year) +
  theme(legend.position="top") +
  labs(color="Group", 
       x="Median income of post code",
       y = "Avg. Nominal Price per Crossing")
# d avg. price per crossing ~ income
plot.to.file = TRUE
if(plot.to.file) {svg("davgprice.byincome.svg", width=7, height=3.5)}
ggplot(pass.veh, aes(x=Med.inc.30.64, y=avg.price.diff, color=expgrp)) +
  #geom_point(alpha=0.25) +    
  geom_smooth() +
  #ylim(-10,10) +
  geom_hline(yintercept=0) +
  labs(color="Group", 
       x="Median income at home post code, SEK",
       y = "Mean Chg. in Avg. Nominal Price/Cross., SEK") +
  scale_x_continuous(labels = scales::comma)
if(plot.to.file) {dev.off()}


# Do some regression modeling for the price variables
mod.tot.price <- lm(avgpricep10 ~ Med.inck.30.64*Year + Med.inck.30.64*expgrp + Year*expgrp, data=veh.year)
summary(mod.tot.price)


mod.avg.price <- lm(avg.price ~ Med.inck.30.64 + expgrp*Year, data=veh.year)
summary(mod.avg.price)


# Do some count models for the integer variables
nb.avg.days <- glm.nb(avg.days ~ expgrp*Year + Med.inck.30.64*expgrp, data=veh.year)
summary(nb.avg.days)

poisson.avg.day.pass <- glm(avg.day.pass ~ Med.inck.30.64*expgrp+Med.inck.30.64*Year+expgrp*Year, family="poisson", data=veh.year)
summary(poisson.avg.day.pass)

# Do logit modeling for any passages

logit.any <- glm(any.pass ~ expgrp*Year+ Med.inck.30.64, 
                 data=veh.year, family=binomial(link="logit"))
summary(logit.any)


# How do ee and rr vary based on income (on a Kommun-basis)?

kommun.inc.ee.rr <- pass.veh %>%
  dplyr::select("Kommun","ee.index","rr.index",
         "Avg.inc.20.29","Avg.inc.30.64","Med.inc.20.29","Med.inc.30.64") %>%
  group_by(Kommun) %>%
  summarize(Avg.inc.20.29=mean(Avg.inc.20.29), Avg.inc.30.64=mean(Avg.inc.30.64),
            Avg.inc.20.29=mean(Avg.inc.20.29), Med.inc.30.64=mean(Med.inc.30.64),
            Avg.ee.index=mean(ee.index), Avg.rr.index=mean(rr.index))


# Aggregate ee and rr indices by Kommun

plot.to.file = TRUE
if(plot.to.file) {svg("rr.byincome.svg", width=3.5, height=3.5)}
ggplot(kommun.inc.ee.rr, aes(x=Med.inc.30.64, y=Avg.rr.index)) +
  geom_point(shape=1) +
  labs(x="Municipality's median income",
       y = "Share of AFVs in total, 2012") +
  scale_x_continuous(labels = scales::comma)
if(plot.to.file) {dev.off()}

plot.to.file = TRUE
if(plot.to.file) {svg("ee.byincome.svg", width=3.5, height=3.5)}
ggplot(kommun.inc.ee.rr, aes(x=Med.inc.30.64, y=Avg.ee.index)) +
  geom_point(shape=1) +
  labs(x="Municipality's median income",
       y = "New registrations as share of total, 2012") +
  scale_x_continuous(labels = scales::comma)
if(plot.to.file) {dev.off()}

# Plot ee and rr against changes in behavior
plot.to.file = TRUE
if(plot.to.file) {svg("ee.bytotprice.svg", width=3.5, height=3.5)}
ggplot(pass.veh, aes(x=totalprice.diff, y=ee.index)) +
  geom_point(shape=1) +
  geom_smooth() +
  labs(x="Change in Total Nominal Price",
       y = "Clean Cars as share of total")
if(plot.to.file) {dev.off()}

plot.to.file = TRUE
if(plot.to.file) {svg("rr.bytotprice.svg", width=3.5, height=3.5)}
ggplot(pass.veh, aes(x=totalprice.diff, y=rr.index)) +
  geom_point(shape=1) +
  geom_smooth() +
  labs(x="Change in Total Nominal Price",
       y = "New registrations as share of total")
if(plot.to.file) {dev.off()}


