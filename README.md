# mma_dashboard

my intention going in:

- scrape some MMA data, because all the buffest guys and the hottest chicks dig MMA data
- attempt to build an analysis dashboard for the resultant data as i have no experience doing this and it seems like an employable skill to have
- maybe try to derive some sense of accomplishment from whatever mess is produced?

For the core of the input data, I have found a pre scraped dataset here:
https://www.kaggle.com/mdabbert/ultimate-ufc-dataset 
(full credit to those guys for putting it together the bunch of top slammers). This is supposedly updated weekly although hasn't been touched in about two months. It was regular before then so I'll give the benefit of the doubt.
Using kaggles API we can pull the latest version prior to each run, though any users will need to authenticate their kaggle account to interact with the API...
  
Beyond this, data on fighter country of origin and training camp is scraped from wikipedia, and fighters disciplines / primary discipline has been manually constructed. I would like in future to build an automated process for constructing this csv as its probably the most useful.

to run, the user must choose to set 'acquire_data' to True (at least in the first instance, in order to get some data to build from) and then hit play on main.py
Once ready, an ip address will be printed in the trace which, when clicked, will lead you to the dashboard. from here the user can choose to plot any two variables for any combination of disciplines. currently the disciplines dont have set colours so make sure to check what each colour represents after each click.
This will produce a scatter plot with LOWESS regression curves plotted for each group where possible. 
Below the scatter plot, is a data table depicting the result of running a chi squared independence test on the LOWESS curves for each group. the intention here is that you will be able to decide whether or not you can draw conclusions about the differences between disciplines based on some combination of the graph and chi squared test.
Below this is a sunburst plot of fight locations over time, which takes the norty liberty of listing US states as countries since they felt comparable to EU member nations to me. tbh this graph feels quite out of place if not useless but hey ho.

Future developments to consider:

- automate disciplines dataset construction via some kind of wikipedia scraper / keyword classifier
- build new graphs with similar depth to the scatter plot. Be nice to utilise more of the available columns if possible, in particular looking at gender / weight class / rank based differences could be interesting
- move some of the content out of the single div its currently saved into in the dashboard as that seems clunky, potentially could re arrange the existing elements into a more elegant layout

For now though I'm going to pause further work on this project to start lookign at something else that's caught my eye. I'm happy to do this as I feel I've gotten what i wanted out of this one (namely I built the dashboard and I now love plotly) 