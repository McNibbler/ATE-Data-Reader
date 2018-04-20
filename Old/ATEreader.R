####################################
# ATE csv/STDF Reader and Analyzer #
# Version 0.1                      #
#                                  #
# February 12, 2018                #
# Thomas Kaunzinger                #
# XCerra Corp.                     #
#                                  #
# References:                      #
# Shiny + shinyFiles Libraries     #
# RADAR Library                    #
####################################

# Libraries
library(shiny)

# Imports the RADAR library because they don't actually have a proper R package
# DOWNLOAD RADAR HERE: https://sites.google.com/site/stdfradar/
my.dir <- getwd()

setwd("./RADAR Files/RADAR_package_0v6p8")
source("Radar.r")

# to change default values, uncomment and adjust the values accordingly:
#tclvalue(.Radar$.TkRadar.env$default_min_plots_per_page) <- 8
#tclvalue(.Radar$.TkRadar.env$default_use_csv_formulas) <- 1
#tclvalue(.Radar$.TkRadar.env$default_use_OOCalc_csv) <- 1
#tclvalue(.Radar$.TkRadar.env$default_add_no4rmal_curve) <- 1

setwd(my.dir)
rm(my.dir)

# Uncomment to use RADAR's default program
TkRadar()


# Testing with this file
#data.dir <- "./Data/"
#data.name <- "super secret test data.std"
#results.name <- "./Data/RDTF/Rtdf Results.rtdf"

#data.rtdf <- ConvertStdf(stdf_name = data.name, rtdf_name = results.name, stdf_dir = data.dir)


# Client side code
ui <- fluidPage(
  
  # Title
  titlePanel("ATE STDF/CSV Processor"),
  
  
  sidebarLayout(
    
    # Uploading the file
    sidebarPanel(
      
      fileInput("file1", h3("STDF/CSV File"),
                accept = c(".std", "text/csv", "text/comma-separated-values,text/plain", ".csv")
      ),
      
      conditionalPanel(
        
        condition = "input.file1 == hello",
        
        h3("nice")
        
        #downloadButton("download.data", "Download")
      )
      
    ),
    
    mainPanel(
      textOutput("filepath1"),
      textOutput("filepath2")
    )
    
  )
  
)


# Server side calculations
server <- function(input, output){
  
  # Jesus Christ STDF files are huge
  # Changed size limit from default 5MB to 50MB
  options(shiny.maxRequestSize=50*1024^2) 
  
  
  # Returns the parameters for the file when it's eventually uploaded
  my.file <- reactive({
    
    if (is.null(input$file1)){
      return(NULL)
    }
    
    input$file1
  
  })
  
  
  # Finds ONLY the filepath with no file (stupid quirk of RADAR needs this I don't know why)
  data.dir <- reactive({
    
    file1 <- toString(my.file()[4])
    
    list1 <- unlist(strsplit(file1,"/"))[0:((length(unlist(strsplit(file1,"/")))) - 1)]

    paste(list1, collapse = '/')
    
  })
  
  
  # Just to make sure I have the filepath actually working. This won't stay for long.
  output$filepath1 <- renderText({
    
    if (is.null(my.file())){
      return(NULL)
    }
    
    paste("Your temp filepath is: ", data.dir())
    
  })
  
  
  # Same thing with the file name
  output$filepath2 <- renderText({
    
    if (is.null(my.file())){
      return(NULL)
    }
    
    paste("Your file is: ", my.file()[1])
    
    
  })
  
  
  
  
  # Jesus I don't know what I'm gonna do here but let's roll with it I guess
  output$download.data <- downloadHandler({
    
    if (is.null(my.file())){
      return(NULL)
    }
    
    ConvertStdf(stdf_name = toString(my.file()[1]), rtdf_name = "data.rtdf", stdf_dir = toString(data.dir()))
    
  })
  
  
}


# Launches the Application
shinyApp(ui, server)