# Scraping the Metal Archive for every metal band on Earth

Easy as a breeze.

We just have to change two parameters of a link: https://www.metal-archives.com/browse/ajax-letter/l/A/json/1?sEcho=3&iColumns=4&sColumns=&iDisplayStart=0&iDisplayLength=1000&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=false&_=1519758159154

We're doing it in python


# Requirements

```bash
pip3 freeze > requirements.txt
```

```bash
pip3 install -r requirements.txt
```

# Run backend
```bash
uvicorn backend:app --reload
```

```commandline
make run
```

# Metrics

```commandline
curl http://127.0.0.1:8001/metrics
```

# Update batch run

```commandline
curl -X POST http://127.0.0.1:8001/api/updater/update
```