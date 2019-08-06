# SequelHelp

Description: This project helps students practice SQL problems by breaking downtheir queries into smaller steps, and displaying the output tables fromeach  step.   This  can  guide  students  by  helping  them  visualize  whateach  step  of  their  query  does  so  they  can  adjust  accordingly  if  their final result does not match the expected result. The number of steps isdetermined by their method of querying, which is described later in theadvanced function.  From the instructor side, there is a question bankmanager, where they can modify, add or delete questions for students to practice and a student manager where they can alter and search the students that are signed up to the website. 

Problem Solved: Due to the natural abstraction of SQL queries, beginners may havea hard time visualizing their queries, and not able to understand their final  output.  Our  project  serves  to  break  complicated  queries  intosmaller steps, whose result will be displayed accordingly.  After brain-storming through various ideas for our advanced functionality, the inspiration was drawn from the idea of the step by step solutions to math problems from Symbolab and Wolfram Alpha. For instance, the following query SELECT Name FROM Employees WHERE Salary >1000;
will be broken down into multiple steps:
SELECT* FROM Employees
SELECT* FROM Employees WHERE Salary >1000;
SELECT Name FROM Employees WHERE Salary >1000;

