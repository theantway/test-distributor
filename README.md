## WHY THIS PROJECT
I found that many projects are getting into a same problem: Long running test. The running time getting longer and longer while more and more tests added into the project. Then developers started to assign tests to different groups using tags and run them in parallel. And the new problem comes: 
* you have to manually change the tags if you want to add more build agents.
* you must decide which group to add when you add new tests

## THE SOLUTION
  Allocate tests to different groups automatically using this tool.

## USAGE
    $ python test_distributor.py --help
    usage: test_distributor.py [-h] -s [TESTS_HISTORY_REPORT_FOLDER] [-n [BLOCKS]]
                               [-p [RESULT_FILENAME_PREFIX]]
                               [-e [RESULT_FILENAME_EXTENSION]] [-d [DEST_FOLDER]]
                               [--delimiter [DELIMITER]]
    
    Assign tests to n blocks for distributed tests.
    
    optional arguments:
      -h, --help            show this help message and exit
      -s [TESTS_HISTORY_REPORT_FOLDER], --source-folder [TESTS_HISTORY_REPORT_FOLDER]
                            source folder which contains history tests reports
                            (default: None)
      -n [BLOCKS], --blocks [BLOCKS]
                            how many blocks to split (default: 1)
      -p [RESULT_FILENAME_PREFIX], --name-prefix [RESULT_FILENAME_PREFIX]
                            base name for the result files (default: tests)
      -e [RESULT_FILENAME_EXTENSION], --name-extension [RESULT_FILENAME_EXTENSION]
                            file extension for the result files (default: txt)
      -d [DEST_FOLDER], --dest-folder [DEST_FOLDER]
                            destination folder for generated files (default: test-
                            blocks)
      --delimiter [DELIMITER]
                            delimiter (default: ,)
    
## Quick Start Using Twist 
   1. Get all tests need to run
        java -jar test-distributor/twist-tests-explorer-1.0.jar -s FunctionalTests/scenarios -t \\'!State-In-Progress\\'

   2. allocate tests to several groups
        java -jar test-distributor/twist-tests-explorer-1.0.jar -s FunctionalTests/scenarios -t \\'!State-In-Progress\\' | python ~/test_distributor.py --source-folder=previous-test-reports --blocks=5 --delimiter=\\'\n\\'

   3. run specified tests
        ant –DscenarioListFile=file_name test

        The execute scenario target in build.xml:
        <target name="execute-scenarios" description="Executes scenarios">
           <path id="scenarios.classpath">
               <path refid="twist.libs" />
               <path refid="user.libs" />
               <path refid="fixtures.classes" />
           </path>
    
           <taskdef classname="com.thoughtworks.twist.core.execution.ant.ExecuteScenariosTask"
                    classpathref="scenarios.classpath" name="twist.runner" description="the Twist ant task" />
           <if>
               <isset property="scenarioListFile"/>
               <then>
                   <fileset dir="${twist.project.dir}/scenarios" includesfile="${scenarioListFile}" id="include.scenarios"/>
               </then>
               <else>
                   <fileset dir="${twist.project.dir}/scenarios" includes="**/*.scn" id="include.scenarios"/>
               </else>
           </if>
    
           <twist.runner scenarioDir="${twist.project.dir}/scenarios" reportsDir="${twist.reports.output.dir}" confDir="${twist.config.dir}"
                          failureproperty="twist.scenarios.failed" classpathref="scenarios.classpath" tags="${twisttags}" threads="1">
               <fileset refid="include.scenarios"/>
           </twist.runner>            
    
           <fail if="twist.scenarios.failed" message="One or more scenarios for failed" />
       </target>

   4. Config the CI to generate test groups in the upstream job, and then run tests in downstream Multi-configuration job (please reference: http://www.theantway.com/2012/04/09/using-multi-configuration-project-for-distributed-builds-on-jenkins/)
   
## References
Please reference the following blog for more information:
* Chinese: http://www.theantway.com/2012/04/13/assign_tests_on_jenkins_based_on_build_history-cn/
* English: work in progress

