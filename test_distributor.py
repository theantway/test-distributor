import argparse
import os
import sys
from xml.etree.ElementTree import ElementTree

class JunitTestReportsParser:
    def __init__(self):
        self.tests_with_time = dict()
        self.tree = ElementTree()

    def parse_history_results(self, reports_folder):
        for dirname, dirnames, filenames in os.walk(reports_folder, onerror=self._on_parse_error):
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

    def _on_parse_error(self, err):
        raise err

class Test:
    def __init__(self, name, time):
        self.name = name
        self.time = time
        self.block = None

class TestBlock:
    def __init__(self, name, average_build_time, max_build_time, is_last_block=False):
        self.name = name
        self.tests = list()
        self.total_time = 0
        self._is_last_block = is_last_block
        self._average_build_time = average_build_time
        self._max_build_time = max_build_time

    def add_test(self, test):
        if self._is_last_block or len(self.tests) == 0 or (self.total_time < self._average_build_time and self.total_time + test.time <= self._max_build_time):
            self.total_time += test.time
            self.tests.append(test)
            test.block = self

class TestDistributor:
    def __init__(self, history_test_time):
        self.tests_with_time = list()
        self.blocks_with_time = list()
        self.history_test_time = history_test_time
        self.default_test_duration = self._default_test_time(history_test_time)
        self.max_seconds_exceed_average = self.default_test_duration/2

    def assign(self, total_blocks, tests):
        self._init_test_time(tests)

        for block_idx in range(1, total_blocks + 1):
            count_of_tests, total_time, average_build_time = self._average_build_time(total_blocks - block_idx + 1, self.tests_with_time)
            max_build_time = average_build_time + self.max_seconds_exceed_average
            print("Estimated total test time {0} seconds, average test time {1} for all {2} tests.".format(str(total_time), str(average_build_time), str(count_of_tests)))
            current_block  = TestBlock(str(block_idx), average_build_time, max_build_time, block_idx == total_blocks)

            for test in self.tests_with_time:
                if test.block is None:
                    current_block.add_test(test)

            self.blocks_with_time.append(current_block)

        return self.blocks_with_time

    def _default_test_time(self, history_test_time):
        return sum(history_test_time.values()) / len(history_test_time) if len(history_test_time) > 0 else 2

    def _get_tests_time(self, test_name):
        if self.history_test_time.has_key(test_name):
            return self.history_test_time[test_name]

        return self.default_test_duration

    def _init_test_time(self, tests):
        for test in tests:
            test = test.strip(' \r\n\.\\\/')
            self.tests_with_time.append(Test(test, self._get_tests_time(test)))

        self.tests_with_time.sort(key=lambda t: t.time, reverse=True)

    def _average_build_time(self, blocks, tests_with_time):
        total_time = 0
        count_of_tests = 0
        for test in tests_with_time:
            if test.block is None:
                total_time += test.time
                count_of_tests +=1

        return count_of_tests, total_time, total_time/blocks

def parse_command_line_args():
    parser = argparse.ArgumentParser(description='Assign tests to n blocks for distributed tests.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-s', '--source-folder', dest='tests_history_report_folder', nargs='?', help='source folder which contains history tests reports', required=True)
    parser.add_argument('-n', '--blocks', dest='blocks', type=int, nargs='?', help='how many blocks to split', default=1)
    parser.add_argument('-p', '--name-prefix', dest='result_filename_prefix', nargs='?', help='base name for the result files', default="tests")
    parser.add_argument('-e', '--name-extension', dest='result_filename_extension', nargs='?', help='file extension for the result files', default='txt')
    parser.add_argument('-d', '--dest-folder', dest='dest_folder', nargs='?', help='destination folder for generated files', default='test-blocks')
    parser.add_argument('--delimiter', dest='delimiter', type=str, nargs='?', help='delimiter', default=',')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_command_line_args()
    parser = JunitTestReportsParser()

    if not os.path.exists(args.dest_folder):
        os.makedirs(args.dest_folder)

    if not os.path.exists(args.tests_history_report_folder):
        print("INFO: History report folder doesn't exists, assigning tests by numbers")
    else:
        parser.parse_history_results(args.tests_history_report_folder)

    tests_to_assign = sys.stdin.readlines()

    distributor = TestDistributor(parser.tests_with_time)
    print("Default test duration is: {0}".format(str(distributor.default_test_duration)))
    blocks = distributor.assign(args.blocks, tests_to_assign)

    delimiter = args.delimiter.decode('string_escape')
    for block in blocks:
        print("\nEstimated time for {0} is: {1}".format(block.name, block.total_time))
        with open(os.path.join(args.dest_folder, "{0}-{1}.{2}".format(args.result_filename_prefix, block.name, args.result_filename_extension)), 'w') as f:
            print(delimiter.join([test.name for test in block.tests]))
            f.write(delimiter.join([test.name for test in block.tests]))
