setForLifeRefined.ipynb is the python data crunching one to visualise trends  
setForLife.py is the AI ChatGPT API version. Need to export the ApiKey first.  
setForLife.csv is the collected data  
setForLifeDataAnalysis.py is for analysing the data, called by setForLife.py  
colours.py makes it all pretty colours  
setForLifeViewing.ipynb is run after setForLifeRefinded.ipynb, to just display the numbers, for using find in chrome to show patterns
  
  
To run, export the ChatGPT Api Key using `export OPENAI_API_KEY=""`  
then run python3 setForLife.py   
It will offer you a set of main balls and a life ball.  
Run the setForLifeRefined.ipynb and view the charts and large dataset so see trends like how many odd/even, how many picked from previous 10 weeks, how many from each bucket etc as well as how many times the ball's been picked, how many weeks since last picked.