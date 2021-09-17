# BigData Management system

A platform for fast and reliable upload, search and export of huge csv files. 
Uses Elasticsearch for storing and searching data, 
Exploites all cpu cores while running queries so that results could be extracted faster

Uses Celery and Redis for background services such as Updating all the previous stored records from a new uploaded file
