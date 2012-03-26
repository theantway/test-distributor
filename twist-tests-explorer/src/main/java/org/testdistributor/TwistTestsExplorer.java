package org.testdistributor;

import com.thoughtworks.twist.core.execution.ant.AndFileFilter;
import com.thoughtworks.twist.core.execution.ant.AutomatedScenarioFilter;
import com.thoughtworks.twist.core.execution.ant.TagFileFilter;

import java.io.File;

public class TwistTestsExplorer {

    private static String scenarioDir = "";
    private static String tags = "";

    public static void main(String[] args) {
        parseCommandLineArguments(args);

        File[] allScenarios = allScenarios(new File(scenarioDir), tags);

        for(File scenario : allScenarios){
            System.out.println(scenario.getName());
        }
    }

    private static void parseCommandLineArguments(String[] args) {
        if (args.length < 2) {
            reportWrongUsage();
        }

        for(int i = 0; i< args.length; i++){
            if(args[i].equals("-s")){
                scenarioDir = args[++i];
            }else if(args[i].equals("-t")){
                tags = args[++i];
            }else{
                reportWrongUsage();
            }
        }
    }

    private static void reportWrongUsage() {
        System.out.println("Usage");
        System.out.println(String.format("java -jar jarFile -s [scenarioDir] [-t tags]"));
        System.exit(-1);
    }

    private static File[] allScenarios(File scenarioDir, String tags) {
        return scenarioDir.getAbsoluteFile().listFiles(filter(tags));
    }

    private static AndFileFilter filter(String tags) {
        return new AndFileFilter(new TagFileFilter(tags), new AutomatedScenarioFilter());
    }

}
