---
title: Web data scraping with Python, Selenium and BeautifulSoup
excerpt_separator: <!--more-->
---

Sometimes the data you want or need is not readily avaialble as a nicely formatted `.csv` file. Sometimes it's an `HTML` table or even worse a convoluted mess of `li` `ul` or `ol` tags.
We might be lucky and be able to copy-paste the table content to an Excel spreadsheet, but what if the table is split in multiple pages? And what if those pages are dynamically filled with Javascript? We would need some browsing capabilities and not just a static page crawler.

For this example, I'll scrape data from a [Plant DNA C-Values Database website](https://cvalues.science.kew.org/search). The website has a search function which dynamically loads data in a table displaying the search result.

<!--more-->
- Table of Contents
{:toc .large-only}
# Static crawling with Javascript
The first and easiest way of getting some data from a table is definitey with Javsacript. It runs on the browser and with the addition of JQuery everything becomes extremely easy.
We could use Javascript on the Chrome developer console.

First and foremost, we need to load JQuery into our Javascript session. Let's open up the Chrome Developer console with `CTRL + SHIFT + J` and type in the following lines
```javascript
var jqry = document.createElement('script');
jqry.src = "https://code.jquery.com/jquery-3.3.1.min.js";
document.getElementsByTagName('head')[0].appendChild(jqry);
jQuery.noConflict();
```

The page might already have JQuery loaded but it might be assigned to a differnt symbol than the usual `$`, so `noConflict()` is helping us in this regard by not overriding the `$`. We can still call jQuery by using the `jQuery()` function.

Next up we need a function to convert the table to a csv file. I have taken inspiration by a pretty nice jQuery plgin called [`table2csv`](https://github.com/OmbraDiFenice/table2csv).
I have added aa `download` function to download the file automatically and edited che code to call it and some default options.

```javascript
jQuery( document ).ready(function($) {
    function download(filename, text) {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/csv;charset=utf8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);

        element.style.display = 'none';
        document.body.appendChild(element);

        element.click();

        document.body.removeChild(element);
    }

    jQuery.fn.table2CSV = function(options) {
            var options = jQuery.extend({
                separator: ',',
                header: [],
                headerSelector: 'th',
                columnSelector: 'td',
                delivery: 'download', // popup, value, download
                filename: 'table.csv', // filename to download
                transform_gt_lt: true // make &gt; and &lt; to > and <
            },
            options);

            var csvData = [];
            var headerArr = [];
            var el = this;

            //header
            var numCols = options.header.length;
            var tmpRow = []; // construct header avalible array

            if (numCols > 0) {
                for (var i = 0; i < numCols; i++) {
                    tmpRow[tmpRow.length] = formatData(options.header[i]);
                }
            } else {
                $(el).filter(':visible').find(options.headerSelector).each(function() {
                    if ($(this).css('display') != 'none') tmpRow[tmpRow.length] = formatData($(this).html());
                });
            }

            row2CSV(tmpRow);

            // actual data
            $(el).find('tr').each(function() {
                var tmpRow = [];
                $(this).filter(':visible').find(options.columnSelector).each(function() {
                    if ($(this).css('display') != 'none') tmpRow[tmpRow.length] = formatData($(this).html());
                });
                row2CSV(tmpRow);
            });
            if (options.delivery == 'popup') {
                var mydata = csvData.join('\n');
                if(options.transform_gt_lt){
                    mydata=sinri_recover_gt_and_lt(mydata);
                }
                return popup(mydata);
            }
            else if(options.delivery == 'download') {
                var mydata = csvData.join('\n');
                if(options.transform_gt_lt){
                    mydata=sinri_recover_gt_and_lt(mydata);
                }
                download(options.filename, mydata);
                //var url='data:text/csv;charset=utf8,' + encodeURIComponent(mydata);
                //window.open(url);
                return true;
            } 
            else {
                var mydata = csvData.join('\n');
                if(options.transform_gt_lt){
                    mydata=sinri_recover_gt_and_lt(mydata);
                }
                return mydata;
            }

            function sinri_recover_gt_and_lt(input){
                var regexp=new RegExp(/&gt;/g);
                var input=input.replace(regexp,'>');
                var regexp=new RegExp(/&lt;/g);
                var input=input.replace(regexp,'<');
                return input;
            }

            function row2CSV(tmpRow) {
                var tmp = tmpRow.join('') // to remove any blank rows
                // alert(tmp);
                if (tmpRow.length > 0 && tmp != '') {
                    var mystr = tmpRow.join(options.separator);
                    csvData[csvData.length] = mystr;
                }
            }
            function formatData(input) {
                // double " according to rfc4180
                var regexp = new RegExp(/["]/g);
                var output = input.replace(regexp, '""');
                //HTML
                var regexp = new RegExp(/\<[^\<]+\>/g);
                var output = output.replace(regexp, "");
                output = output.replace(/&nbsp;/gi,' '); //replace &nbsp;
                if (output == "") return '';
                return '"' + output.trim() + '"';
            }
            function popup(data) {
                var generator = window.open('', 'csv', 'height=400,width=600');
                generator.document.write('<html><head><title>CSV</title>');
                generator.document.write('</head><body >');
                generator.document.write('<textArea cols=70 rows=15 wrap="off" >');
                generator.document.write(data);
                generator.document.write('</textArea>');
                generator.document.write('</body></html>');
                generator.document.close();
                return true;
            }
        };
});
```
Now for the final touch, just call this line on the result of your search and it will conver the table to a .csv file and automatically download it or you. Pretty cool uh?

```javascript
jQuery( document ).ready(function($) {
     jQuery("table.search-results").table2CSV();
});
```
There are quite a few limitations with this approach:
- Everytime the page reloads we need to re-run the code above
- We need to do this manually for each page of the table

# Dynamic web scraping with Python and Selenium
Now that we sort of know where the data is and how to extract it we can think of how to automate this process.
The most common tools for web scraping are `selenium` and `beautifulSoup` packages for python.

Getting Selenium to work should be a post of its own but for now let's assume you followed [this guide](https://selenium-python.readthedocs.io/installation.html) and that everything is working.
I am using `Anaconda3` so I simply ran:
```bash
conda install -c anaconda beautifulsoup4 request selenium
```

I then downloaded the Chrome WebDriver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and extracted it to `C:\chromedriver\chromedriver.exe`.

**HEADS UP**: Make sure your Chrome driver version matches your installed Chrome version. For instance: I was using Chrome 84 but the chrome driver was for Chrome 85, I just updated my Chrome and it all worked perfectly.
{:.message}

Now that we all set up, let's start by opening our page:

```python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import time
import csv


url = "https://cvalues.science.kew.org/search"
# Create a new Chrome session
driver = webdriver.Chrome('C:\\chromedriver\\chromedriver.exe') # I am using Chrome on Windows so I need to specify the path
driver.implicitly_wait(0.1)
driver.get(url) # Navigate to the page
titme.sleep(30) # Give the user some time to see the page at least
driver.close()
```

This code is fairly simple: Create a new Chrome session, navigate to the page, wait for 30 seconds and then close it.
But what about `implicitly_wait()`? This line sets the amount of time Selenium waits for an element before throwing an Exception. So calling `findElement()` will throw an exception after 0.1 seconds if the element is not found. Remembe that this line *sets* the waiting time. So you only need to call it once to sets the time for the whole session until the browser is closed.

When we open the link we provide you will notice there is no table but only a bunch of paramters we can set to filter our search. Now we could:
- Program our script to fill in these parameters and let selenium click the search button
- Let the user fill the search parameters on the web page and then click search

The second approach has the pros of saving us a lot of time and headaches especially in case the structure of the form changes. The only thing we should be careful about is to make sure Selenium knows when the search button has been clicked and when to start scraping the data from the table.

The easiest way I found is to just have a loop that constantly checks for the presence of the table of results.

```python
while True:
    tabResults = None # This will contain the table container, it's initially None since we haven't found it yet
    try:
        tabResults = driver.find_element_by_id("tabResults") # Try to find the tabResults which is the table container
    except Exception as e:
        continue # If there was an exception then the table was not found so we should skip the next part and re-start the loop
    ...# extract the data
```
The code is pretty self explanatory: Try to get the table container and if this throws an exception (due to the `implicitly_wait()`) restart the loop. If there is not exception and tabResults is not None then do something.

Let's create some functions to extract the data from the table:

```python
def rowToCsvSel(columns, csvwriter):  
    tdRow = []  
    for td in columns:
        tdRow.append(td.text)
        referenceData = td.find_elements_by_css_selector("a")
        if len(referenceData) > 0:
            tdRow.append(referenceData[0].get_attribute("data-content"))

    if len(tdRow) > 0:
        csvwriter.writerow(tdRow)
        return 1
    return 0

def getTableDataSel(tabResults):
    global currentResult
    global looping
    global currentFileIndex
    global csvfile
    global wr
    numbers = re.findall(r'\d+', tabResults.find_element_by_css_selector("h1").text)
    # print(numbers)
    fromRes = int(numbers[0])
    toRes = int(numbers[1])
    total = int(numbers[2])  
    if fromRes <= 1:
        currentResult = fromRes
        looping = True
        csvfile = open('plants_data{}.csv'.format(currentFileIndex), 'w', newline='', encoding='utf-8') # Getting the handle to the file, I need to specify UTF-8 since the table contains UTF characters
        wr = csv.writer(csvfile) # Getting the csv writer with the file associated
    table =  tabResults.find_element_by_class_name("search-results")
    if looping:
        for row in table.find_elements_by_css_selector('tr'):
            driver.implicitly_wait(0) # Without this it will just hang since the td elements might not have been loaded
            print("Result {} of {}".format(currentResult, total))
            if currentResult <= 1:                
                rowToCsvSel(row.find_elements_by_css_selector('th'), wr)
            currentResult += rowToCsvSel(row.find_elements_by_css_selector('td'), wr)
    if toRes >= total:
        if looping:
            print("Data collection completed!")
            currentFileIndex += 1
        looping = False
    return currentResult

```

There is a lot to explain here but let's go step by step:
- The global variables are just a way to keep track of what's happening and
