#!/usr/bin/env Rscript

library(devtools)
library(CausalImpact)

args = commandArgs(trailingOnly=TRUE)

data_file <- args[1]
pre_period_start <- args[2]
pre_period_end <- args[3]
post_period_start <- args[4]
post_period_end <- args[5]

# Read in data, separated by ,
ts_data <- read.csv(file=data_file,head=TRUE,sep=",")

# Dates should be YYYY-MM-DD. May need to revisit for hour...
ts_data$date <- as.Date(ts_data$date, format="%Y-%m-%d")

# Set NAs to 0
ts_data[is.na(ts_data)] <- 0

# Set pre and post periods
pre.period <- as.Date(c(pre_period_start, pre_period_end))
post.period <- as.Date(c(post_period_start, post_period_end))

### IMPORTANT -- HARDCODED FOR NOW
### Will figure this out later...

emotion.sadness <- "emotion.sadness"
target.emotion.sadness <- "target.emotion.sadness"

# Join up data...first is Y and remaining are x1, x2, x3...
impact_input <- zoo(cbind(ts_data[target.emotion.sadness], ts_data[emotion.sadness]), ts_data$date)

# Do the magic
impact_output <- CausalImpact(impact_input, pre.period, post.period)

# THIS NEEDS TO BE WIDE ENOUGH FOR OUTPUT!!!
options(width=1000)

# Both of these are picked up by python process as the outputs
cat(paste(impact_output$summary$AbsEffect[2],"\n"))
print(impact_output$series)

# Let's save the charts for now as well
mypath <- paste("/src/image_outputs/","emotion.png", sep="")
png(mypath)
    plot(impact_output)
dev.off()


