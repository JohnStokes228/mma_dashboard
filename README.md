# mma_dashboard

my intention going in:

- scrape some MMA data, because all the buffest guys and the hottest chicks dig MMA data
- attempt to build an analysis dashboard for the resultant data as i have no experience doing this and it seems like an employable skill to have
- maybe try to derive some sense of accomplishment from whatever mess is produced?

For the core of the input data, I have found a pre scraped dataset here:
https://www.kaggle.com/mdabbert/ultimate-ufc-dataset 
(full credit to those guys for putting it together the bunch of top slammers). This is supposedly updated weekly although hasn't been touched in about two months. It was regular before then so I'll give the benefit of the doubt.
Using kaggles API we can pull the latest version prior to each run, but this will obviously need to be logged. Any users will need to authenticate their kaggle account to interact with the API...
  
I have also scraped wikipedia for the remaining desired data. the code used to do this has been copied out of my webscraping project and into here to allow it to also be regularly run / updated.
I may yet choose to build a crawler to scrape each fighters wikipedia bio and then attempt to automatically classify that fighters disciplines from there, but failing that for now we will use a manually reated data file for this.

NEXT UP:

- analise the per fighter dataset I've created to get a feel for important visualisations we may want on the dashboard
- decide how to build this fatty dashboard
- learn dash / plotly libraries
- build a main script that will give the user control of the creation of the dashboard
- build the data collection into an input to the main pipeline
- write further unit tests, especially of spider functions
