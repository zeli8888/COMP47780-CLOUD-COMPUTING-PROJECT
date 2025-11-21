# Hadoop Docker Container
```bash
docker run -d -p 9870:9870 -p 8088:8088 -p 8080:8080 -p 18080:18080 -p 9000:9000 -p 8888:8888 -p 9864:9864 -v ${PWD}:/root/ipynb --name cc-spark-jupyter-pig zeli8888/spark-jupyter-pig
```

## explanation
```text
-p 9870:9870    # NameNode Web UI →  NameNode 
-p 9000:9000    # HDFS RPC
-p 8088:8088    # ResourceManager Web UI →  ResourceManager, yarn service
-p 9864:9864    # DataNode Web UI →  DataNode
-p 8080:8080    # Spark Master UI →  Spark Master
-p 18080:18080  # Spark History Server →  Spark History Server
-p 8888:8888    # Jupyter Notebook UI →  Jupyter 
```

## access container
```bash
docker exec -it cc-spark-jupyter-pig /bin/bash
```

## access jupyter notebook
```bash
http://localhost:8888
```

# CCProject Compilation
## Requirement
- JDK17
- MAVEN 3.9.6
## Compilation
```bash
cd ccproject && mvn clean package && cp target/ccproject-1.0-SNAPSHOT.jar ./ && cd ..
```

# Dashboard
## Requirement
```bash
conda create -n cc-project python=3.11
conda activate cc-project
```
```bash
cd dashboard && pip install -r requirements.txt && cd ..
```
## Start Dashboard
```bash
cd dashboard && streamlit run medical_dashboard.py
```
## Access Web
```bash
http://localhost:8501
```

# Current Issues
1. walk through plots
2. verify sms received data
3. High-Risk Age Groups (TOP5) title change
4. Health Conditions Detailed Data missing 4 diseases
6. cross validate the analysis data generated