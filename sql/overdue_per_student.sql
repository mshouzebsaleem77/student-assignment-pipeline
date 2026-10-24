SELECT student_id,student_name,SUM(is_overdue) AS overdue_count,SUM(is_late) AS late_submission_count
FROM silver_student_assignments GROUP BY student_id,student_name ORDER BY student_id;
