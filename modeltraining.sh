echo "Starting Batch" && \
cd /data/enshield-apis && \
echo pwd && \
source /data/enshield-apis/enshieldapienv/bin/activate && \
echo "Virtual Env Activated" && \
python3 train.py && \
echo "Training Batch Completed"
