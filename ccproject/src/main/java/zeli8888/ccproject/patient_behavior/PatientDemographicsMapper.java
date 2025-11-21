package zeli8888.ccproject.patient_behavior;

import java.io.IOException;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;

public class PatientDemographicsMapper extends Mapper<Object, Text, Text, IntWritable> {

    private final static IntWritable one = new IntWritable(1);
    private Text analysisKey = new Text();

    @Override
    public void map(Object key, Text value, Context context) {

        String line = value.toString();
        String[] fields = line.split(",");

        if (fields[0].equals("PatientId")) {
            return;
        }
        // PatientId,AppointmentID,Gender,ScheduledDay,AppointmentDay,Age,Neighbourhood,Scholarship,Hipertension,Diabetes,Alcoholism,Handcap,SMS_received,No-show

        try {
            String gender = fields[2].trim(); // Gender
            String scheduledDay = fields[3].trim(); // ScheduledDay
            String appointmentDay = fields[4].trim(); // AppointmentDay
            String ageStr = fields[5].trim(); // Age
            String neighbourhood = fields[6].trim(); // Neighbourhood
            String hypertension = fields[8].trim(); // Hipertension
            String diabetes = fields[9].trim(); // Diabetes
            String alcoholism = fields[10].trim(); // Alcoholism
            String handicap = fields[11].trim(); // Handcap
            String smsReceived = fields[12].trim(); // SMS_received
            String noShow = fields[13].trim(); // No-show

            // Validate data completeness
            if (gender.isEmpty() || ageStr.isEmpty() || noShow.isEmpty() ||
                    scheduledDay.isEmpty() || appointmentDay.isEmpty()) {
                return;
            }

            int age;
            try {
                age = Integer.parseInt(ageStr);
                if (age < 0 || age > 120)
                    return; // Filter invalid ages
            } catch (NumberFormatException e) {
                return;
            }

            String attendanceStatus = noShow.equalsIgnoreCase("Yes") ? "NoShow" : "Attended";

            // === 1. Scheduling Lead Time Analysis ===
            boolean valid = analyzeSchedulingLeadTime(context, scheduledDay, appointmentDay, attendanceStatus);
            if (!valid) {
                return; // Skip further analysis for invalid lead time records
            }

            // === 2. Gender Dimension Analysis ===
            analyzeByGender(context, gender, attendanceStatus);

            // === 3. Age Dimension Analysis ===
            analyzeByAge(context, age, attendanceStatus);

            // === 4. Neighborhood Dimension Analysis ===
            analyzeByNeighbourhood(context, neighbourhood, attendanceStatus);

            // === 5. Health Condition Dimension Analysis ===
            analyzeByHealthCondition(context, hypertension, diabetes, alcoholism, handicap, attendanceStatus);

            // === 6. SMS Reminder Effectiveness Analysis ===
            analyzeSMSReminder(context, smsReceived, attendanceStatus);

        } catch (Exception e) {
            // Log error but continue processing other records
            context.getCounter("DATA_QUALITY", "MALFORMED_RECORDS").increment(1);
        }
    }

    /**
     * Gender Dimension Analysis
     */
    private void analyzeByGender(Context context, String gender, String attendanceStatus)
            throws IOException, InterruptedException {
        analysisKey.set("GENDER_" + gender + "_" + attendanceStatus);
        context.write(analysisKey, one);
    }

    /**
     * Age Dimension Analysis
     */
    private void analyzeByAge(Context context, int age, String attendanceStatus)
            throws IOException, InterruptedException {
        String ageGroup = categorizeAge(age);

        // Age group vs attendance behavior
        analysisKey.set("AGE_GROUP_" + ageGroup + "_" + attendanceStatus);
        context.write(analysisKey, one);

        // Detailed age range analysis (10-year intervals)
        String detailedAgeGroup = getDetailedAgeGroup(age);
        analysisKey.set("DETAILED_AGE_" + detailedAgeGroup + "_" + attendanceStatus);
        context.write(analysisKey, one);
    }

    /**
     * Neighborhood Dimension Analysis
     */
    private void analyzeByNeighbourhood(Context context, String neighbourhood, String attendanceStatus)
            throws IOException, InterruptedException {
        if (!neighbourhood.isEmpty() && !neighbourhood.equals("NULL")) {
            analysisKey.set("NEIGHBOURHOOD_" + neighbourhood + "_" + attendanceStatus);
            context.write(analysisKey, one);
        }
    }

    /**
     * Health Condition Dimension Analysis
     */
    private void analyzeByHealthCondition(Context context, String hypertension, String diabetes,
            String alcoholism, String handicap, String attendanceStatus)
            throws IOException, InterruptedException {

        // Single disease analysis
        if (hypertension.equals("1")) {
            analysisKey.set("HEALTH_HYPERTENSION_" + attendanceStatus);
            context.write(analysisKey, one);
        }

        if (diabetes.equals("1")) {
            analysisKey.set("HEALTH_DIABETES_" + attendanceStatus);
            context.write(analysisKey, one);
        }

        if (alcoholism.equals("1")) {
            analysisKey.set("HEALTH_ALCOHOLISM_" + attendanceStatus);
            context.write(analysisKey, one);
        }

        if (!handicap.equals("0")) {
            analysisKey.set("HEALTH_HANDICAP_" + attendanceStatus);
            context.write(analysisKey, one);
        }

        // Healthy population analysis
        boolean isHealthy = hypertension.equals("0") && diabetes.equals("0") &&
                alcoholism.equals("0") && handicap.equals("0");
        if (isHealthy) {
            analysisKey.set("HEALTH_HEALTHY_" + attendanceStatus);
            context.write(analysisKey, one);
        }

        // Multiple diseases analysis
        int diseaseCount = countDiseases(hypertension, diabetes, alcoholism, handicap);
        if (diseaseCount >= 2) {
            analysisKey.set("HEALTH_MULTIPLE_DISEASES_" + diseaseCount + "_" + attendanceStatus);
            context.write(analysisKey, one);
        }
    }

    /**
     * Scheduling Lead Time Analysis
     * Analyzes the relationship between appointment lead time and attendance
     */
    private boolean analyzeSchedulingLeadTime(Context context, String scheduledDay,
            String appointmentDay, String attendanceStatus)
            throws IOException, InterruptedException {
        long leadTimeDays = calculateLeadTimeDays(scheduledDay, appointmentDay);
        if (leadTimeDays < 0) {
            return false; // Invalid lead time
        }
        String leadTimeCategory = categorizeLeadTime(leadTimeDays);

        // Lead time vs attendance behavior
        analysisKey.set("LEAD_TIME_" + leadTimeCategory + "_" + attendanceStatus);
        context.write(analysisKey, one);
        return true;
    }

    /**
     * SMS Reminder Effectiveness Analysis
     */
    private void analyzeSMSReminder(Context context, String smsReceived, String attendanceStatus)
            throws IOException, InterruptedException {
        String smsStatus = smsReceived.equals("1") ? "SMS_RECEIVED" : "NO_SMS";
        analysisKey.set("SMS_" + smsStatus + "_" + attendanceStatus);
        context.write(analysisKey, one);
    }

    /**
     * Calculate lead time in days between scheduled and appointment dates
     */
    private long calculateLeadTimeDays(String scheduledDay, String appointmentDay) {
        // Extract just the date part (first 10 characters: "YYYY-MM-DD")
        String scheduledDate = scheduledDay.substring(0, 10);
        String appointmentDate = appointmentDay.substring(0, 10);

        // Parse dates directly from YYYY-MM-DD format
        LocalDate scheduled = LocalDate.parse(scheduledDate);
        LocalDate appointment = LocalDate.parse(appointmentDate);

        return ChronoUnit.DAYS.between(scheduled, appointment);
    }

    /**
     * Categorize lead time into meaningful groups
     */
    private String categorizeLeadTime(long leadTimeDays) {
        if (leadTimeDays == 0)
            return "SAME_DAY";
        else if (leadTimeDays <= 3)
            return "SHORT";
        else if (leadTimeDays <= 7)
            return "MEDIUM";
        else if (leadTimeDays <= 30)
            return "LONG";
        else if (leadTimeDays <= 90)
            return "VERY_LONG";
        else
            return "EXTREMELY_LONG";
    }

    /**
     * Age categorization
     */
    private String categorizeAge(int age) {
        if (age <= 18)
            return "CHILDREN_YOUTH";
        else if (age <= 35)
            return "YOUNG_ADULTS";
        else if (age <= 55)
            return "MIDDLE_AGED";
        else
            return "SENIORS";
    }

    /**
     * Detailed age grouping
     */
    private String getDetailedAgeGroup(int age) {
        int groupStart = (age / 10) * 10;
        int groupEnd = groupStart + 9;
        return groupStart + "-" + groupEnd;
    }

    /**
     * Count number of diseases/conditions
     */
    private int countDiseases(String hypertension, String diabetes, String alcoholism, String handicap) {
        int count = 0;
        if (hypertension.equals("1"))
            count++;
        if (diabetes.equals("1"))
            count++;
        if (alcoholism.equals("1"))
            count++;
        if (!handicap.equals("0"))
            count++;
        return count;
    }
}