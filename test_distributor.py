import os
from xml.etree.ElementTree import ElementTree
import sys

class JunitTestReportsParser:
    def __init__(self):
        self.tests_with_time = dict()
        self.tree = ElementTree()

    def parse_history_results(self, reports_folder):
        for dirname, dirnames, filenames in os.walk(reports_folder):
            for subdirname in dirnames:
                self.parse_history_results(os.path.join(dirname, subdirname))

            for filename in filenames:
                filepath = os.path.join(dirname, filename)
                if not filename.endswith(".xml"):
                    continue

                name, time = self._parse_file(filepath)
                self.tests_with_time[name] = time

    def _parse_file(self, report_file):
        self.tree.parse(report_file)
        suite = self.tree.getroot()
        return suite.attrib["name"], float(suite.attrib["time"])

class Test:
    def __init__(self, name, time):
        self.name = name
        self.time = time
        self.block = None

class TestBlock:
    def __init__(self, name):
        self.name = name
        self.tests = list()
        self.total_time = 0

    def add_test(self, test):
        self.total_time += test.time
        self.tests.append(test)
        test.block = self

class TestDistributor:
    def __init__(self, history_test_time):
        self.tests_with_time = list()
        self._difference = 20
        self.blocks_with_time = list()
        self.history_test_time = history_test_time

    def assign(self, total_blocks, tests):
        self._init_test_time(tests)
        average_build_time = self._average_build_time(total_blocks, self.tests_with_time)
        max_build_time = average_build_time + self._difference
        print("Estimated average test time: " + str(average_build_time))

        for block_idx in range(1, total_blocks + 1):
            current_block  = TestBlock(str(block_idx))
            for test in self.tests_with_time:
                if test.block is None:
                     if block_idx == total_blocks or len(current_block.tests) == 0 or current_block.total_time + test.time <= max_build_time:
#                         print("added test {0} to block {1}".format(test.name, block_idx))
                         current_block.add_test(test)

            self.blocks_with_time.append(current_block)

        for block in self.blocks_with_time:
#            pprint.PrettyPrinter(indent=4).pprint(self.blocks_with_time)
            print(block.name)
            for test in block.tests:
                print(test.name)

        return self.blocks_with_time

    def _get_tests_time(self, test_name):
        if self.history_test_time.has_key(test_name):
            return self.history_test_time[test_name]
        return 60

    def _init_test_time(self, tests):
        for test in tests:
            test = test.strip(' \r\n\.\\\/')
            self.tests_with_time.append(Test(test, self._get_tests_time(test)))

        self.tests_with_time.sort(key=lambda t: t.time, reverse=True)
        for test in self.tests_with_time:
            print("test {0} time: {1}".format(test.name, test.time))

    def _average_build_time(self, blocks, tests_with_time):
        total_time = 0
        for test in tests_with_time:
            total_time += test.time

        print("Estimated total test time: " + str(total_time))
        return total_time/blocks

if __name__ == '__main__':
    blocks = 8
    target_folder = "/testrepo"
    tests_to_assign = sys.stdin.readlines()

    parser = JunitTestReportsParser()
    parser.parse_history_results("/testrepo")
    #            print(parser.tests)

    distributor = TestDistributor(parser.tests_with_time)
    blocks = distributor.assign(blocks, tests_to_assign)

    for block in blocks:
        print("Estimated time for {0} is: {1}".format(block.name, block.total_time))
        f = open(os.path.join(target_folder, "function-{0}.txt".format(block.name)), 'w')
        print(",".join([test.name for test in block.tests]))
        f.write(",".join([test.name for test in block.tests]))
        f.close()

