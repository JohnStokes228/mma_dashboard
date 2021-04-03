# mma_dashboard

my intention going in:

- scrape some MMA data, because all the buffest guys and the hottest chicks dig MMA data
- attempt to build an anlysis dashboard for the resultant data (plotly? streamlit?) as i have no experience doing this and it seems like an employable skill to have
- maybe look into some kind of database solution for the data?
- maybe try to answer some meaningful questions this time?
- maybe try to derive some sense of accomplishment from whatever mess is produced?
- to take the rest of the code to the next level, I'd like to implement pep8 in the docstrings and pytest for the unit tests

guess first step to all of this is to scrape the data, I think some websites worth starting to look in might be:

- http://ufcstats.com/statistics/fighters
- https://www.sherdog.com/events 

sherdog has stats from fights / fighters outside the ufc. its T&Cs aso dont claim they will stop you from scraping whereas ufcstats does. unfortunately, ufcstats appears to be the better datasource for per fight breakdowns. I think I'll need to decide on what the dashboard is *for* before I am able to finalise which of the two I will scrape. may as well write spiders for both though right, just in case ;) 

I think once we've scraped, it might be worth seeing if any kind of cleaning / classifying / general wrangling work on the data can be built into a pipeline since that also seems quite useful and given the nture of the sport as an ongoing narative it makes sense that any given data set that i produce wouldnt be like the *final* dataset but rather just the current one.
