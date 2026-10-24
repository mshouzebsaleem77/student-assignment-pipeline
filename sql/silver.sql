CREATE TABLE silver_student_assignments AS
WITH first_submission AS (
 SELECT student_id, assignment_id, MIN(submitted_at) AS submitted_at
 FROM silver_submissions WHERE submitted_at <= :as_of
 GROUP BY student_id, assignment_id
)
SELECT s.student_id,s.student_name,s.email,c.course_id,c.course_name,
 a.assignment_id,a.assignment_name,a.due_at,f.submitted_at,
 CASE WHEN f.submitted_at IS NOT NULL THEN 1 ELSE 0 END AS is_submitted,
 CASE WHEN a.due_at < :as_of AND f.submitted_at IS NULL THEN 1 ELSE 0 END AS is_overdue,
 CASE WHEN f.submitted_at > a.due_at THEN 1 ELSE 0 END AS is_late
FROM silver_students s JOIN silver_courses c ON s.course_id=c.course_id
JOIN silver_assignments a ON a.course_id=c.course_id
LEFT JOIN first_submission f ON f.student_id=s.student_id AND f.assignment_id=a.assignment_id;
