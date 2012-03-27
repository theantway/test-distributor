package org.testdistributor;

import org.hamcrest.core.Is;
import org.hamcrest.core.IsNot;
import org.hamcrest.core.IsNull;
import org.junit.Test;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.core.Is.is;
import static org.junit.Assert.assertThat;

public class JUnitTestExplorerTest {
    @Test
    public void should_get_the_current_test_classes() {
        Class<?>[] classes = JUnitTestExplorer.searchTestClasses(true, new String[]{".*Test"});
        assertThat(classes, IsNull.notNullValue());
        assertThat(classes.length, greaterThan(0));
        assertThat(classes[0].getName(), is(this.getClass().getName()));
    }
}
