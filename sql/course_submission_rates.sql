SELECT course_id,course_name,COUNT(*) AS expected_submissions,
SUM(is_submitted) AS submitted_count,ROUND(100.0*SUM(is_submitted)/COUNT(*),2) AS submission_rate_pct
FROM silver_student_assignments GROUP BY course_id,course_name ORDER BY course_id;
