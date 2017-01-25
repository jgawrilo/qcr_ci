#!/usr/bin/env Rscript
#install.packages(c("devtools"), repos="http://cran.us.r-project.org", dependencies=TRUE)
library(devtools)
#devtools::install_github("google/CausalImpact")
library(CausalImpact)

#anyNA <- function(x) any(is.na(x))
#library("ggplot2")

args = commandArgs(trailingOnly=TRUE)

x <- args[1]
#output_path <- args[2]
pre_period_start <- args[2]
pre_period_end <- args[3]
post_period_start <- args[4]
post_period_end <- args[5]

ts_data <- read.csv(file=x,head=TRUE,sep=",")
ts_data$date <- as.Date(ts_data$date, format="%Y-%m-%d")
ts_data[is.na(ts_data)] <- 0

pre.period <- as.Date(c(pre_period_start, pre_period_end))
post.period <- as.Date(c(post_period_start, post_period_end))

anger <- "emotion.anger"
angry <- "emotion.angry"
fear <- "emotion.fear"

# Raw ISIS Counts
#data <- zoo(cbind(ts_data$target_isis_perc, ts_data$isis_perc), ts_data$date)
data <- zoo(cbind(ts_data[anger], ts_data[angry], ts_data[fear]), ts_data$date)

impact <- CausalImpact(data, pre.period, post.period)
options(width=1000)

#print()
#mypath <- paste(output_path,"guy_isis.png", sep="")
#fileConn<-file(paste(output_path,"datas/","guy_isis.txt",sep=""))
#writeLines(paste("guy",impact$summary$AbsEffect[2]), fileConn)
#close(fileConn)

cat(paste(impact$summary$AbsEffect[2],"\n"))
print(impact$series)

#png(mypath)
#    plot(impact)
#dev.off()


