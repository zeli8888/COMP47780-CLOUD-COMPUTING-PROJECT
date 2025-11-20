package zeli8888.ccproject.patient_behavior;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class PatientDemographicsAnalysis {

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: PatientDemographicsAnalysis <input path> <output path>");
            System.err.println("Example: PatientDemographicsAnalysis /patient_no_show_analysis/raw_data /patient_no_show_analysis/results/patient_demographics");
            System.exit(-1);
        }

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Patient Demographics and No-Show Analysis");

        job.setJarByClass(PatientDemographicsAnalysis.class);
        job.setMapperClass(PatientDemographicsMapper.class);
        job.setCombinerClass(PatientDemographicsReducer.class);
        job.setReducerClass(PatientDemographicsReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        System.out.println("Starting Patient Demographics Analysis Job...");
        System.out.println("Input Path: " + args[0]);
        System.out.println("Output Path: " + args[1]);

        long startTime = System.currentTimeMillis();
        boolean success = job.waitForCompletion(true);
        long endTime = System.currentTimeMillis();

        if (success) {
            System.out.println("Job completed successfully!");
            System.out.println("Execution Time: " + (endTime - startTime) + " ms");

            org.apache.hadoop.mapreduce.Counters counters = job.getCounters();
            System.out.println("Malformed Records: " +
                    counters.findCounter("DATA_QUALITY", "MALFORMED_RECORDS").getValue());
        } else {
            System.out.println("Job failed!");
            System.exit(1);
        }

        System.exit(0);
    }
}