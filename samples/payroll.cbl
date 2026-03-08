       IDENTIFICATION DIVISION.
       PROGRAM-ID. PAYROLL-CALC.
       AUTHOR. LEGACY-SYSTEMS-CORP.

      *--------------------------------------------------
      * Payroll Calculation Program
      * Calculates gross pay, tax deduction, and net pay
      * for hourly employees.
      *--------------------------------------------------

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-EMPLOYEE-NAME        PIC X(30) VALUE SPACES.
       01  WS-HOURS-WORKED         PIC 9(3)V9(2) VALUE ZEROS.
       01  WS-HOURLY-RATE          PIC 9(5)V9(2) VALUE ZEROS.
       01  WS-GROSS-PAY            PIC 9(7)V9(2) VALUE ZEROS.
       01  WS-OVERTIME-HOURS       PIC 9(3)V9(2) VALUE ZEROS.
       01  WS-OVERTIME-PAY         PIC 9(7)V9(2) VALUE ZEROS.
       01  WS-TAX-RATE             PIC 9(1)V9(4) VALUE 0.2000.
       01  WS-TAX-DEDUCTION        PIC 9(7)V9(2) VALUE ZEROS.
       01  WS-NET-PAY              PIC 9(7)V9(2) VALUE ZEROS.
       01  WS-OVERTIME-THRESHOLD   PIC 9(3) VALUE 40.
       01  WS-OVERTIME-MULTIPLIER  PIC 9(1)V9(1) VALUE 1.5.
       01  WS-CONTINUE-FLAG        PIC X VALUE 'Y'.

       PROCEDURE DIVISION.
       MAIN-PARA.
           PERFORM UNTIL WS-CONTINUE-FLAG = 'N'
               PERFORM GET-EMPLOYEE-DATA
               PERFORM CALCULATE-PAY
               PERFORM DISPLAY-RESULTS
               DISPLAY "Process another employee? (Y/N): "
               ACCEPT WS-CONTINUE-FLAG
           END-PERFORM
           STOP RUN.

       GET-EMPLOYEE-DATA.
           DISPLAY "Enter Employee Name: "
           ACCEPT WS-EMPLOYEE-NAME
           DISPLAY "Enter Hours Worked: "
           ACCEPT WS-HOURS-WORKED
           DISPLAY "Enter Hourly Rate: "
           ACCEPT WS-HOURLY-RATE.

       CALCULATE-PAY.
           IF WS-HOURS-WORKED > WS-OVERTIME-THRESHOLD
               COMPUTE WS-OVERTIME-HOURS =
                   WS-HOURS-WORKED - WS-OVERTIME-THRESHOLD
               COMPUTE WS-OVERTIME-PAY =
                   WS-OVERTIME-HOURS * WS-HOURLY-RATE *
                   WS-OVERTIME-MULTIPLIER
               COMPUTE WS-GROSS-PAY =
                   (WS-OVERTIME-THRESHOLD * WS-HOURLY-RATE) +
                   WS-OVERTIME-PAY
           ELSE
               COMPUTE WS-GROSS-PAY =
                   WS-HOURS-WORKED * WS-HOURLY-RATE
           END-IF
           COMPUTE WS-TAX-DEDUCTION =
               WS-GROSS-PAY * WS-TAX-RATE
           COMPUTE WS-NET-PAY =
               WS-GROSS-PAY - WS-TAX-DEDUCTION.

       DISPLAY-RESULTS.
           DISPLAY "=================================="
           DISPLAY "PAYROLL SUMMARY"
           DISPLAY "=================================="
           DISPLAY "Employee    : " WS-EMPLOYEE-NAME
           DISPLAY "Hours Worked: " WS-HOURS-WORKED
           DISPLAY "Hourly Rate : $" WS-HOURLY-RATE
           DISPLAY "Gross Pay   : $" WS-GROSS-PAY
           DISPLAY "Tax (20%)   : $" WS-TAX-DEDUCTION
           DISPLAY "Net Pay     : $" WS-NET-PAY
           DISPLAY "==================================".
