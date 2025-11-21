# COMP47780 Cloud Computing Project Deployment Guide

## 🌐 Remote Deployment - Amazon EMR Cluster
*(Results already saved, optional execution, may incur minimal charges)*

### Data Extraction
```bash
unzip data/archive.zip -d data/ && mv data/KaggleV2-May-2016.csv data/medical_appointments.csv
```

### AWS CLI Installation & Configuration
Install AWS CLI following official documentation:
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

**Configure AWS credentials:**
```bash
aws configure
```

### Authentication
```bash
aws sts get-caller-identity
```

### Create S3 Bucket & Upload Data
```bash
aws s3 mb s3://zeli8888-cc-project --region eu-west-1 \
&& aws s3 cp ./data/medical_appointments.csv s3://zeli8888-cc-project/ \
&& aws s3 cp ./ccproject/ccproject-1.0-SNAPSHOT.jar s3://zeli8888-cc-project/ \
&& aws s3 ls s3://zeli8888-cc-project/
```

### Create EMR Cluster & Run Job
**Remove previous results (if any):**
```bash
aws s3 rm s3://zeli8888-cc-project/results/ --recursive
```

**Create default roles (if they don't exist):**
```bash
aws emr create-default-roles
```

**Create EMR cluster and run job:**
```bash
aws emr create-cluster \
    --name "CC-Hadoop-Project" \
    --release-label emr-6.15.0 \
    --instance-type m4.large \
    --instance-count 1 \
    --use-default-roles \
    --region eu-west-1 \
    --auto-terminate \
    --steps Type=CUSTOM_JAR,Name=PatientAnalysis,Jar=s3://zeli8888-cc-project/ccproject-1.0-SNAPSHOT.jar,Args=[zeli8888.ccproject.patient_behavior.PatientDemographicsAnalysis,s3://zeli8888-cc-project/medical_appointments.csv,s3://zeli8888-cc-project/results/]
```

### Monitor Cluster & Job Status
**List active clusters:**
```bash
aws emr list-clusters --active --region eu-west-1
```

**Get cluster ID and set as environment variable:**
```bash
export CLUSTER_ID=YOUR_CLUSTER_ID
```

**Monitor job steps:**
```bash
aws emr list-steps --cluster-id $CLUSTER_ID --region eu-west-1
```

**Wait for job completion and cluster auto-termination:**
```bash
aws emr describe-cluster --cluster-id $CLUSTER_ID --region eu-west-1 --query 'Cluster.[Status.State, Status.Timeline.EndDateTime]'
```

![Remote Deployment Screenshot](demo/remote.png)

### Retrieve Results
```bash
aws s3 cp s3://zeli8888-cc-project/results/part-r-00000 ./aws_emr_results.txt && cat aws_emr_results.txt
```

**Clean up S3 bucket:**
```bash
aws s3 rb s3://zeli8888-cc-project --force --region eu-west-1
```

## 📊 Online Dashboard Analysis
**Access URL: https://zeli8888-cc-medical-dashboard.streamlit.app/**

---

## 💻 Local Deployment

### Run Hadoop Analysis
*(Results already saved, optional execution)*

### Data Extraction
```bash
unzip data/archive.zip -d data/ && mv data/KaggleV2-May-2016.csv data/medical_appointments.csv
```

### Start Hadoop Container
*(Large image size, suitable for learning and local testing)*
```bash
docker run -d -p 9870:9870 -p 8088:8088 -p 8080:8080 -p 18080:18080 -p 9000:9000 -p 8888:8888 -p 9864:9864 -v ${PWD}:/root/ipynb --name cc-spark-jupyter-pig zeli8888/spark-jupyter-pig
```

### Access Container
```bash
docker exec -it cc-spark-jupyter-pig /bin/bash
```

### Upload Dataset to HDFS
```bash
hdfs dfs -mkdir -p /patient_no_show_analysis/raw_data \
&& hdfs dfs -put -f /root/ipynb/data/medical_appointments.csv /patient_no_show_analysis/raw_data/ \
&& hdfs dfs -rm -r /patient_no_show_analysis/results/patient_demographics 2>/dev/null
```

### Run Analysis Job
```bash
hadoop jar /root/ipynb/ccproject/ccproject-1.0-SNAPSHOT.jar \
    zeli8888.ccproject.patient_behavior.PatientDemographicsAnalysis \
    /patient_no_show_analysis/raw_data \
    /patient_no_show_analysis/results/patient_demographics
```

### Retrieve Results
```bash
hdfs dfs -get -f /patient_no_show_analysis/results/patient_demographics/part-r-00000 /root/ipynb/patient_demographics_results.txt
```

## 📈 Local Dashboard Analysis
```bash
docker run -d -p 8501:8501 -v ./patient_demographics_results.txt:/app/patient_demographics_results.txt --name cc-dashboard zeli8888/cc-medical-dashboard
```

**Access URL: http://localhost:8501**

## 🎬 Demo Screenshots
![Local Demo 1](demo/local_1.png)
![Local Demo 2](demo/local_2.png)
![Local Demo 3](demo/local_3.png)
![Local Demo 4](demo/local_4.png)
![Local Demo 5](demo/local_5.png)
![Local Demo 6](demo/local_6.png)
![Local Demo 7](demo/local_7.png)
![Local Demo 8](demo/local_8.png)