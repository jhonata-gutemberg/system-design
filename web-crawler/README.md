# Web crawler
## Context
A **web crawler**, also known as a **spider** or **bot**, is a program or automated script that systematically browses the internet to **index and collect data** from websites.
### Common Uses
* **Search engines (e.g., Googlebot):** To keep search indexes up to date.
* **Data mining / web scraping:** To extract specific data, such as prices or news articles.
* **Web monitoring:** Monitor **SEO metrics** (e.g., broken links, slow-loading pages)
* **Web archiving:** It's how you can view what a website looked like in the past (e.g., CNN’s homepage in 2005).
## Requirements
### Functional
- [x] Should download all the web pages addressed by the URL list
- [x] Should extract URLs from these pages
- [x] Should add to the list of URLs to be downloaded
- [ ] Should consider newly added or edited web pages
- [ ] Duplicated content should be ignored
### Non functional
- [x] Should be able to handle 1 billion pages per month
- [x] Need to store HTML pages up to 5 years
- [ ] High scalable
- [ ] Robustness
- [ ] Politeness
- [ ] Extensibility

## Back of the envelope
![Average](https://latex.codecogs.com/png.image?\large&space;\dpi{100}\bg{white}Average\;web\;page\;size=500kb)

![QPS](https://latex.codecogs.com/png.image?\large&space;\dpi{100}\bg{white}QPS=\frac{1billon_{requests/day}}{30_{days}*24_{hours}*3600_{seconds}}\cong400)

![Peak QPS](https://latex.codecogs.com/png.image?\large&space;\dpi{100}\bg{white}QPS_{peak}=2*QPS=800)

![Storage](https://latex.codecogs.com/png.image?\large&space;\dpi{100}\bg{white}Storage\;capacity=1billion_{requests/day}*500kb_{average\;web\;page\;size}*12_{months}*\5_{years}=30_{PB})

## Architecture
![Web crawler](assets/web-crawler.excalidraw.png)
The web crawling starts by adding a list of URL's (seeds) to the queue url.frontier, this queue will be consumed by multiple workers that will download the HTML from the pages, check if the content already exists on the content storage, extract the links, apply filters, check if the link was already seen on the URL storage and add the new links to the url.frontier. The crawler algorithm can be implemented with BFS (Breadth First Search).
### Freshness
To consider newly added or edited web pages, we can recrawl from time to time, based on web page's update history and prioritize URLs, by recrawling important pages first and more frequently.
