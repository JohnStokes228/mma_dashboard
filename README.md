# mma_dashboard
This project is to build some kind of visualisation dashboard for some so far undefined MMA data that I'll need to source from somewhere at some point...

my intention going in:

- scrape some MMA data, because all the buffest guys and the hottest chicks dig MMA data
- attempt to build an analysis dashboard for the resultant data (plotly? streamlit?) as i have no experience doing this and it seems like an employable skill to have
- maybe look into some kind of database solution for the data?
- maybe try to derive some sense of accomplishment from whatever mess is produced?
- to take the rest of the code to the next level, I'd like to implement pep484 in the docstrings, pytest for the unit tests and sphinx for documentation

In case i decide to scrape the data later, I think some websites worth starting to look in might be:

- http://ufcstats.com/statistics/fighters
- https://www.sherdog.com/events 

sherdog has stats from fights / fighters outside the ufc. its T&Cs aso dont claim they will stop you from scraping whereas ufcstats does. unfortunately, ufcstats appears to be the better datasource for per fight breakdowns. I think I'll need to decide on what the dashboard is *for* before I am able to finalise which of the two I will scrape. may as well write spiders for both though right, just in case ;) 

I think once we've scraped, it might be worth seeing if any kind of cleaning / classifying / general wrangling work on the data can be built into a pipeline since that also seems quite useful and given the nature of the sport as an ongoing narative it makes sense that any given data set that i produce wouldnt be like the *final* dataset but rather just the current one.


scratch the scraping for now, theres an up to date kaggle dataset that looks like it might at least get me started - its built on a per fight dynamically updating basis though so I'll have to buil a method of converting it to fighter based statistics which adds to the charm ey ;)
this dataset is located by here https://www.kaggle.com/mdabbert/ultimate-ufc-dataset full credit to those guys for putting it together the bunch of top slammers. 
I have actually scraped some extra bits from wikipedia for the sake of completeness by now...

I had hoped to scrape some data from ea ufc4 to give me per fighter disciplines but unfortunately the size of the roster, coupled with the number of duplicate fighters and the inaccuracy of some values (10 khabibs who are all judoka?) I ended up manually mapping the fighters disciplines based on their wikipedia articles.
In future I may write some code to scrape the fighter bios from wikipedia or something and automatically extract the disciplines but for now this manual method will do and didnt take toooo long.



NEXT UP:

- analise the per fighter dataset I've created to get a feel for important visualisations we may want on the dashboard
- decide how to build this fatty dashboard
- learn dash / plotly libraries
- build a main script that will give the user control of the creation of the dashboard
