/*
 * @author Johannes Link (business@johanneslink.net)
 * 
 * Published under GNU General Public License 2.0 (http://www.gnu.org/licenses/gpl.html)
 */
package org.junit.extensions.cpsuite;

public class ClasspathFinderFactory implements ClassesFinderFactory {

	public ClassesFinder create(boolean searchInJars, String[] filterPatterns, SuiteType[] suiteTypes, Class<?>[] baseTypes, Class<?>[] excludedBaseTypes, String classpathProperty) {
		ClassTester tester = new ClasspathSuiteTester(searchInJars, filterPatterns, suiteTypes, baseTypes, excludedBaseTypes);
		return new ClasspathClassesFinder(tester, classpathProperty);
	}

}
