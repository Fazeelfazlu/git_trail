cd /data/enshield-apis &&
export https_proxy=http://185.46.212.90:443 &&
export HF_HOME=/data/libraries_download &&
export NLTK_DATA=/data/nltk_data &&
export TRANSFORMERS_OFFLINE=1 &&
source /data/enshield-apis/enshieldapienv/bin/activate && 
gunicorn --config /data/enshield-apis/gunicorn_config.py main:app
