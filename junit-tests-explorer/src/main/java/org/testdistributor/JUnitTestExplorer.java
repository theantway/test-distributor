package org.testdistributor;

import org.junit.extensions.cpsuite.ClassesFinder;
import org.junit.extensions.cpsuite.ClassesFinderFactory;
import org.junit.extensions.cpsuite.ClasspathFinderFactory;
import org.junit.extensions.cpsuite.SuiteType;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class JUnitTestExplorer {
    public static void main(String[] args) {
        boolean searchInJars = true;
        String[] classNameFilterPatterns = new String[]{".*Tests", ".*Test"};

        Class<?>[] testclasses = searchTestClasses(searchInJars, classNameFilterPatterns);

        for (Class<?> clazz : testclasses) {
            System.out.println(clazz.getName());
        }
    }

    public static Class<?>[] searchTestClasses(boolean searchInJars, String[] classNameFilterPatterns) {
        SuiteType[] suiteTypes = new SuiteType[]{SuiteType.TEST_CLASSES, SuiteType.RUN_WITH_CLASSES, SuiteType.JUNIT38_TEST_CLASSES};
        Class<?>[] baseTypes = new Class<?>[] { Object.class };
        Class<?>[] excludeBaseTypes = new Class<?>[0];
        String classpathProperty="cp";

        ClassesFinder finder = new ClasspathFinderFactory().create(searchInJars, classNameFilterPatterns, suiteTypes, baseTypes, excludeBaseTypes, classpathProperty);
        return getSortedTestclasses(finder);
    }

    private static Class<?>[] getSortedTestclasses(ClassesFinder finder) {
        List<Class<?>> testclasses = finder.find();
        Collections.sort(testclasses, getClassComparator());
        return testclasses.toArray(new Class[testclasses.size()]);
    }

    private static Comparator<Class<?>> getClassComparator() {
        return new Comparator<Class<?>>() {
            public int compare(Class<?> o1, Class<?> o2) {
                return o1.getName().compareTo(o2.getName());
            }
        };
    }

}

