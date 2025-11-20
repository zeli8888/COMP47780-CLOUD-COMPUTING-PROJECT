# Deploy locally
## Unzip data
```bash
unzip data/archive.zip -d data/ && mv data/KaggleV2-May-2016.csv data/medical_appointments.csv
```
## Start Hadoop Container
```bash
docker run -d -p 9870:9870 -p 8088:8088 -p 8080:8080 -p 18080:18080 -p 9000:9000 -p 8888:8888 -p 9864:9864 -v ${PWD}:/root/ipynb --name cc-spark-jupyter-pig zeli8888/spark-jupyter-pig
```
## Go into container
```bash
docker exec -it cc-spark-jupyter-pig /bin/bash
```
## Upload dataset to HDFS
```bash
hdfs dfs -mkdir -p /patient_no_show_analysis/raw_data \
&& hdfs dfs -mkdir -p /patient_no_show_analysis/results/patient_demographics \
&& hdfs dfs -put /root/ipynb/data/medical_appointments.csv /patient_no_show_analysis/raw_data/
```