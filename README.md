### Collector for COD Datasets
[![Build Status](https://travis-ci.org/OCHA-DAP/hdx-scraper-cods.svg?branch=master&ts=1)](https://travis-ci.org/OCHA-DAP/hdx-scraper-cods) [![Coverage Status](https://coveralls.io/repos/github/OCHA-DAP/hdx-scraper-cods/badge.svg?branch=master&ts=1)](https://coveralls.io/github/OCHA-DAP/hdx-scraper-cods?branch=master)

This script connects to the [COD API]() and extracts data from each dataset creating a dataset per country in HDX. The scraper takes around 20 minutes to run. It makes in the order of 200 reads from the COD API and 1000 read/writes (API calls) to HDX in total. It does not create temporary files as it puts urls into HDX. It is run monthly. 


### Usage

    python run.py

For the script to run, you will need to have a file called .hdx_configuration.yml in your home directory containing your HDX key eg.

    hdx_key: "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    hdx_read_only: false
    hdx_site: prod
    
 You will also need to supply the universal .useragents.yml file in your home directory as specified in the parameter *user_agent_config_yaml* passed to facade in run.py. The collector reads the key **hdx-scraper-cods** as specified in the parameter *user_agent_lookup*.
 
 Alternatively, you can set up environment variables: USER_AGENT, HDX_KEY, HDX_SITE, EXTRA_PARAMS, TEMP_DIR, LOG_FILE_ONLY