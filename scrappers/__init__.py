import scrappers.saudia_arabia.saudia_arabia_scrapper as sa
all_scrappers ={
    "sa":{
        "module":sa, # refers to the module, not as important as the function
        "scrap_function":sa.scrap, # refers to the scrapping function which is very important
        "scrap_database": "scrap_database", # storage properties
        "scrap_collection": "scraps", # storage properties
        "scrap_document": "sa-doc", # storage properties
        "title": "Saudia Arabia", # display option
        "description": "Some description of the endpoints our api will scrap over.." # storage properties
    },
}