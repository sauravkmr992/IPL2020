
# IPL2020

Scraping and analyzing the **IPL2020** data.

Data has been scraped out from [ESPN cricinfo](https://www.espncricinfo.com/series/ipl-2020-21-1210595/match-results) using [Scrapy](https://scrapy.org/).

	
	Scraping

	Steps to run the script:
	
		1. Conda/pip install scrapy version listed in the requirements and all the other dependencies.
		2. Now, move folder IPL2020 to your local machine.
		3. Activate the environment then move into IPL2020 folder from your terminal/cmd.
		4. Type 'scrapy crawl matches.py -o ipl.csv'
		5. This will generate a csv file named  "ipl" having 120 rows and 30 columns.
		

	► Scraped csv file is inside first IPL2020 folder.
	► response_format.json contains json response structure seeing which the scraping code has been written.

	Note : In the python script, you might find the url different than the url mentioned above. It is beacuse "API" url has been used instead of main url.
	
	       1. Visit the ESPN cricinfo link above. Select one of the matches.
	       2. Press ctrl+shift+i to open the developer tools.
	       3. Go to the "Network" tab and then "Fetch/XHR".
	       4. Reload the page again to see all the requests. You may find the request I have used to scrape the content.
	       5. Request looks like this (https://hs-consumer-api.espncricinfo.com/v1/pages/match/scorecard?lang=en&seriesId=1210595&matchId=1237181).
	       
	
	Analysis
	
	- Analysis is done on the data through pandas and seaborn library to find meaningful information or the pattern if any.
	- Analysis is done by asking questions and answering them using Pandas.
	- You can find the ipynb script in the repo having name 'ipl2020analysis.ipynb'.


You can find the python file used for scraping in the folder structure as follows:
 - IPL2020
   - IPL2020
     - spiders
       - matches.py



