# Deploy locally
## Run Hadoop (results already saved, optional)
### Unzip Data
```bash
unzip data/archive.zip -d data/ && mv data/KaggleV2-May-2016.csv data/medical_appointments.csv
```
### Start Hadoop Container (large image, for learning and local test)
```bash
docker run -d -p 9870:9870 -p 8088:8088 -p 8080:8080 -p 18080:18080 -p 9000:9000 -p 8888:8888 -p 9864:9864 -v ${PWD}:/root/ipynb --name cc-spark-jupyter-pig zeli8888/spark-jupyter-pig
```
### Go into Container
```bash
docker exec -it cc-spark-jupyter-pig /bin/bash
```
### Upload Dataset to HDFS
```bash
hdfs dfs -mkdir -p /patient_no_show_analysis/raw_data \
&& hdfs dfs -put -f /root/ipynb/data/medical_appointments.csv /patient_no_show_analysis/raw_data/ \
&& hdfs dfs -rm -r /patient_no_show_analysis/results/patient_demographics 2>/dev/null
```
### Run Analysis Jobs
```bash
hadoop jar /root/ipynb/ccproject/ccproject-1.0-SNAPSHOT.jar \
    zeli8888.ccproject.patient_behavior.PatientDemographicsAnalysis \
    /patient_no_show_analysis/raw_data \
    /patient_no_show_analysis/results/patient_demographics
```

### Get Results
```bash
hdfs dfs -get -f /patient_no_show_analysis/results/patient_demographics/part-r-00000 /root/ipynb/dashboard/patient_demographics_results.txt
```

## Dashboard Analysis

## Demo

# Deploy on AWS
