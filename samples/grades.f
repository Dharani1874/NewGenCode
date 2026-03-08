C     ================================================
C     FORTRAN PROGRAM: STUDENT GRADE CALCULATOR
C     Reads student scores, computes average, assigns grade
C     ================================================
      PROGRAM GRADES
      INTEGER NSTUDENTS, I, SCORE
      REAL TOTAL, AVERAGE
      CHARACTER*30 SNAME
      CHARACTER*1 GRADE

      TOTAL = 0.0
      NSTUDENTS = 0

      WRITE(*,*) 'Enter number of students:'
      READ(*,*) NSTUDENTS

      DO 100 I = 1, NSTUDENTS
          WRITE(*,*) 'Enter student name:'
          READ(*,'(A)') SNAME
          WRITE(*,*) 'Enter score (0-100):'
          READ(*,*) SCORE

          TOTAL = TOTAL + SCORE

          IF (SCORE .GE. 90) THEN
              GRADE = 'A'
          ELSE IF (SCORE .GE. 80) THEN
              GRADE = 'B'
          ELSE IF (SCORE .GE. 70) THEN
              GRADE = 'C'
          ELSE IF (SCORE .GE. 60) THEN
              GRADE = 'D'
          ELSE
              GRADE = 'F'
          END IF

          WRITE(*,*) 'Student: ', SNAME
          WRITE(*,*) 'Score  : ', SCORE
          WRITE(*,*) 'Grade  : ', GRADE
          WRITE(*,*) '----------------------------'
  100 CONTINUE

      IF (NSTUDENTS .GT. 0) THEN
          AVERAGE = TOTAL / NSTUDENTS
          WRITE(*,*) 'Class Average: ', AVERAGE
      ELSE
          WRITE(*,*) 'No students entered.'
      END IF

      STOP
      END
