library(Rcpp)
library(Rblpapi)
library(chron)
library(xts)
library(quantmod)
library(TTR)
library(RColorBrewer)
require(PerformanceAnalytics)
library(PortfolioAnalytics)
require(reshape2)
require(lattice)
require(latticeExtra)
require(plyr)
require(scales)
require(zoo)
library(rlang)
library(tibble)
require(ggplot2)

setwd("C:\\Users\\ruledaV\\OneDrive - Manulife\\Rates_Scorecard_R\\")

carry_input <- "C:\\Users\\ruledaV\\OneDrive - Manulife\\Portfolio_Carry_Model\\"
carry_data <- "C:\\Users\\ruledaV\\OneDrive - Manulife\\Portfolio_Carry_Model\\data\\"
carry_perf <- "C:\\Users\\ruledaV\\OneDrive - Manulife\\Portfolio_Carry_Model\\perf\\"
outputpath <- "C:\\Users\\ruledaV\\OneDrive - Manulife\\Rates_Scorecard_R\\results\\"

curve_data <- 'curves.csv'

curves <- read.csv(paste(carry_input,curve_data,sep=''),sep=",",stringsAsFactors =F)
curves_live <- curves

curves_freq <- c(4,2,2,2,2,2,4,4,4)


con <- blpConnect() 

ifelse(as.POSIXlt(Sys.Date())$wday == 1,end <- Sys.Date() -3,end <- Sys.Date() -1)
start <- end  #as.Date('2017-01-05') #Sys.Date() - 260*5

curve_tickers <- c('ADFS','CDFS','SFFS','EUSA','BPSWS', 'JYSO','NDFS','SKFS','USFS')
spot_tickers <- c('ADSW','CDSW','SFSNT','EUSA','BPSWS','JYSO','NDSW','SKSW','USSW')
#spot_tickers <- sub('FS','SW',curve_tickers) #dropped this when libor changed tickers

tenors <- seq(from = 1, to = 30, by= 1)
tenors <- ifelse(tenors < 10, paste(0,tenors,sep=''),tenors)

fwds <- as.data.frame(paste(expand.grid(tenors,tenors)[,1],'y',expand.grid(tenors,tenors)[,2],'y',sep=''))
names(fwds)[1] <- 'point'

fwds$code <- paste(substr(fwds$point,1,2),substr(fwds$point,4,5),sep='')
fwds$start <- as.numeric(substr(fwds$code,1,2))
fwds$mat <- as.numeric(substr(fwds$code,1,2))+as.numeric(substr(fwds$code,3,4))
fwds <- subset(fwds,mat <=30)
fwds$rollto <- paste(as.numeric(substr(fwds$point,1,2))-1,substr(fwds$point,4,5),sep='')
fwds$rollto <- ifelse(nchar(fwds$rollto)==3,paste(0,fwds$rollto,sep=''),fwds$rollto)

fwds$rolltostart <- as.numeric(substr(fwds$rollto,1,2))
fwds$rolltomat <- as.numeric(substr(fwds$rollto,1,2))+as.numeric(substr(fwds$rollto,3,4))

data_tenors <- c(seq(from = 1, to = 10, by = 1),15,20,25,30) # these will be the liquid data points that we will get from Bloomberg
fwds$point <- as.character(fwds$point)
fwds_template <- fwds

### Get spot curve data ###

i <- 1
for (i in 1:length(curve_tickers)) {
  
  #get the spot data
  z <- 1
  for (z in 1:length(tenors)) {
    
    ifelse(is.element(as.numeric(tenors)[z],data_tenors),    spot_data <- bdh(paste(spot_tickers[i],as.numeric(tenors)[z],' curncy',sep=''), "PX_LAST", start.date=start, end.date=end),spot_data <- as.data.frame(cbind(end,NA)))
    names(spot_data)[1] <- 'date'
    ifelse(z==1,spot_curve <- spot_data,spot_curve <- merge(spot_curve,spot_data,by='date',all.x=T,all.y=T))
    
    names(spot_curve)[z+1] <- paste(names(curves)[i+1],'_',tenors[z],sep='')
    
    z <- z + 1
  }
  
### Fit curve using cubic spine ###
  
plot(as.numeric(spot_curve[,2:length(spot_curve)]) ~ tenors,ylab='rate',main=curve_tickers[i])
  
spot_curve_fit <- na.spline(as.numeric(spot_curve[,2:length(spot_curve)]), tenors)
lines(spot_curve_fit,col='red')

spot_curve[,2:length(spot_curve)] <- spot_curve_fit

  #combine the spot data
  ifelse(i==1,combined_spot <- as.numeric(t(spot_curve[2:length(spot_curve)])),combined_spot <- cbind(combined_spot,as.numeric(t(spot_curve[2:length(spot_curve)]))))
  
  i <- i + 1
}

combined_spot <- as.data.frame(combined_spot)
names(combined_spot) <- colnames(curves_live)[2:ncol(curves_live)]


### Calculate zero rates ###

combined_zero <- 1+(sweep(combined_spot,2,curves_freq,"/") / 100)
compounding <-sweep(do.call("rbind", replicate(30, curves_freq, simplify = FALSE)),1,as.numeric(tenors),"*")
combined_zero <- 1/(combined_zero ^ compounding)

### Calculate implied forwards ###


b <- 1
fwds <- fwds_template
fwds$fwd <- NA
fwds$spot <- NA

for (b in 1:ncol(combined_spot)) {
  
a <- 1
for (a in 1:nrow(fwds)) {

  fwds$fwd[a] <- (log(combined_zero[fwds$start[a],b])-log(combined_zero[fwds$mat[a],b]))*(1/(fwds$mat[a]-fwds$start[a]))*100
  
  if (fwds$rolltostart[a] == 0){
    
    fwds$fwdnext[a] <- combined_spot[fwds$rolltomat[a],b]
    } else {
      
      fwds$fwdnext[a] <- (log(combined_zero[fwds$rolltostart[a],b])-log(combined_zero[fwds$rolltomat[a],b]))*(1/(fwds$rolltomat[a]-fwds$rolltostart[a]))*100
    
  }
  
fwds$spot[a] <-  combined_spot[as.numeric(substr(fwds$point[a],4,5)),b]
  
a <- a + 1}

fwds$rolldown <- fwds$fwd - fwds$fwdnext
fwds$fwdvspot <- fwds$fwd - fwds$spot

ifelse(b==1,combined_rolldown <- fwds[,c("point","rolldown")],combined_rolldown<-cbind(combined_rolldown,fwds$rolldown))
names(combined_rolldown)[b+1] <- names(combined_spot)[b]

ifelse(b==1,combined_steepness <- fwds[,c("point","fwdvspot")],combined_steepness<-cbind(combined_steepness,fwds$fwdvspot))
names(combined_steepness)[b+1] <- names(combined_spot)[b]

ifelse(b==1,combined_fwd <- fwds[,c("point","fwd")],combined_fwd<-cbind(combined_fwd,fwds$fwd))
names(combined_fwd)[b+1] <- names(combined_spot)[b]



b <- b+1
}

write.table(combined_rolldown,file=paste(outputpath,"combined_rolldown.csv",sep=''),sep=",",row.names=F)
write.table(combined_steepness,file=paste(outputpath,"combined_steepness.csv",sep=''),sep=",",row.names=F)
write.table(combined_fwd,file=paste(outputpath,"combined_fwd.csv",sep=''),sep=",",row.names=F)


#back up 
all_rolldown <- combined_rolldown

# Trades like 7y1y etc are quite leveraged and will have wide bid/offer so will filter by a ratio of start/maturity

combined_rolldown$ratio_1 <- abs(as.numeric(substr(combined_rolldown$point,1,2)) / as.numeric(substr(combined_rolldown$point,4,5)))
combined_rolldown$ratio_2 <- abs(as.numeric(substr(combined_rolldown$point,4,5)) / as.numeric(substr(combined_rolldown$point,1,2)))


combined_rolldown$filter <- ifelse((combined_rolldown$ratio_1 + combined_rolldown$ratio_2) <= 5,1,0)

combined_rolldown <- subset(combined_rolldown,combined_rolldown$filter == 1)
combined_rolldown <- combined_rolldown[,1:(ncol(combined_rolldown)-3)]
####


rolldown_rank <- rank(as.matrix(combined_rolldown[,2:ncol(combined_rolldown)]))

rolldown_rank_top <- ifelse(rolldown_rank <=5,1,ifelse(rolldown_rank >= (length(rolldown_rank)-4),1,0))

stretch <- function(x, sep="_", saveAttrs=NULL, matrixReturn=FALSE) #Pat Burns function
{
  if(is.matrix(x)) {
    result <- setNames(c(x), c(outer(rownames(x), colnames(x), paste, sep=sep)))
  } else if(is.data.frame(x)) {
    result <- setNames(unlist(x), c(outer(rownames(x), colnames(x), paste, sep=sep)))
  } else {
    stop("don't know how to stretch this type of object")
  }
  if(matrixReturn) result <- as.matrix(result)
  if(length(saveAttrs)) {
    attributes(result) <- c(attributes(result), attributes(x)[saveAttrs])
  }
  result
}
rownames(combined_rolldown) <- combined_rolldown$point
st_com_roll <- stretch(combined_rolldown[, -1])

rolldown_bottom <- as.data.frame(st_com_roll[rank(st_com_roll) <= 30])
names(rolldown_bottom) <- 'bp'
rolldown_top <- as.data.frame(st_com_roll[rank(st_com_roll) >= (length(rolldown_rank)-4)])
names(rolldown_top) <- 'bp'

best_rolldown <- rbind(rolldown_bottom,rolldown_top)
best_rolldown <- as.data.frame(cbind(rownames(best_rolldown),best_rolldown))



mat_constraint <- 10 #Add constraint to the total maturity of the swap



best_rolldown$bp_abs <- abs(best_rolldown$bp)

best_rolldown_ordered <-best_rolldown[order(-best_rolldown$bp_abs),]
best_rolldown_ordered$ccy <- substr(best_rolldown_ordered[,1],8,11)

ccy_constraint <- 2 # Limit number of positions in each currency

g <- 1
ccy_list <- 'NA'

for (g in 1:nrow(best_rolldown_ordered)) {

if (sum(ccy_list==best_rolldown_ordered$ccy[g]) < ccy_constraint) {
  
ccy_list <- cbind(ccy_list,best_rolldown_ordered$ccy[g])
ifelse(g==1,best_rolldown_constrained <- best_rolldown_ordered[g,], best_rolldown_constrained <- rbind(best_rolldown_constrained,best_rolldown_ordered[g,]))

}

g <- g + 1 }

names(best_rolldown_constrained)[1] <- 'point'

best_rolldown_constrained$pos <- ifelse(best_rolldown_constrained$bp >0,1,-1)

total_rollbp <- sum(best_rolldown_constrained$bp_abs)
total_rollrisk <- sum(best_rolldown_constrained$pos)

best_rolldown_constrained$bp_abs <- NULL

best_rolldown_constrained$bp <- round(best_rolldown_constrained$bp,2)


##Hedged Yields###################








##################################




### Produce PDF of results ###


pdf(paste(outputpath,"Carry_Optimisation.pdf",sep=''),title="Absolute Return - Portfolio Optimisation",family="Courier")


### Plot the curves ###

combined_spot_plot <- cbind(tenors,combined_spot)
melted_a = melt(combined_spot_plot, id.vars="tenors")
ggplot(data=melted_a, aes(x=tenors, y=value, group=variable,color=variable)) + geom_line(size=2) 

#combined_steep_plot <- cbind(fwds$point,combined_steepness[,2:ncol(combined_steepness)])
#combined_steep_plot <-(subset(combined_steep_plot,substr(combined_steep_plot[,1],1,2)=="01"))
#melted_b = melt(combined_steep_plot, id.vars="fwds$point")
#ggplot(data=melted_b, aes(x=melted_b[,1], y=value, group=variable,color=variable)) + geom_line(size=2)

combined_fwd_plot <- cbind(fwds$point,combined_fwd[,2:ncol(combined_fwd)])
combined_fwd_plot <-(subset(combined_fwd_plot,substr(combined_fwd_plot[,1],1,2)=="01"))
melted_c = melt(combined_fwd_plot, id.vars="fwds$point")
#ggplot(data=melted_c, aes(x=melted_c[,1], y=value, group=variable,color=variable)) + geom_line(size=2)


par(mfrow=c(2,2)) 
    
p <- 1

for (p in 1:(ncol(combined_fwd_plot)-1)) {

  limit_max <- max(c(max(combined_fwd_plot[,p+1]),max(combined_spot[,p])))
  limit_min <- min(c(min(combined_fwd_plot[,p+1]),min(combined_spot[,p])))
  
plot(combined_fwd_plot[,p+1],type='l',col='green',xlab='tenor',ylab='rate',main=paste(colnames(combined_fwd_plot)[p+1],' fwd 1y (green) vs. spot (red)',sep=''),ylim=c(limit_min,limit_max)  )
  
lines(combined_spot[,p],type='l',col='red')


p <- p + 1 }



###

par(mfrow=c(1,1))

textplot(best_rolldown_constrained[, !(colnames(best_rolldown_constrained) %in% c("bp_abs"))],show.rownames = F)
title(paste('Risk = ',total_rollrisk,' Year(s), Roll total = ',round(total_rollbp*100,0),sep=''))

dev.off()



