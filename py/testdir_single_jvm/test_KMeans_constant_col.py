import unittest, random, sys, time
sys.path.extend(['.','..','py'])
import h2o, h2o_cmd, h2o_hosts, h2o_browse as h2b, h2o_import2 as h2i
import h2o_kmeans
import h2o_exec as h2e

def write_syn_dataset(csvPathname, rowCount, colCount, SEED):
    r1 = random.Random(SEED)
    dsf = open(csvPathname, "w+")

    for i in range(rowCount):
        rowData = []
        for j in range(colCount):
            # make the first col constant to see what KMeans does for centers
            if j == 0:
                r = 0
            else:
                r = random.randint(0,2)
            rowData.append(r)

        rowDataCsv = ",".join(map(str,rowData))
        dsf.write(rowDataCsv + "\n")

    dsf.close()


class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global SEED, localhost
        SEED = h2o.setup_random_seed()
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(1,java_heap_GB=4)
        else:
            h2o_hosts.build_cloud_with_hosts()

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_KMeans_constant_col(self):
        SYNDATASETS_DIR = h2o.make_syn_dir()
        tryList = [
            (100, 11, 'cA', 5),
            (100, 10, 'cB', 5),
            (100, 9, 'cC', 5),
            (100, 8, 'cD', 5),
            (100, 7, 'cE', 5),
            (100, 6, 'cF', 5),
            (100, 5, 'cG', 5),
            ]

        ### h2b.browseTheCloud()
        lenNodes = len(h2o.nodes)

        cnum = 0
        for (rowCount, colCount, hex_key, timeoutSecs) in tryList:
            print "Generate synthetic dataset with first column constant = 0 and see what KMeans does"
            cnum += 1
            csvFilename = 'syn_' + str(SEED) + "_" + str(rowCount) + 'x' + str(colCount) + '.csv'
            csvPathname = SYNDATASETS_DIR + '/' + csvFilename

            print "Creating random", csvPathname
            write_syn_dataset(csvPathname, rowCount, colCount, SEED)
            parseResult = h2i.import_parse(path=csvPathname, schema='put', hex_key=csvFilename + ".hex")
            print "Parse result['destination_key']:", parseResult['destination_key']

            kwargs = {'k': 2, 'initialization': 'Furthest', 'cols': None, 'destination_key': 'benign_k.hex'}
            kmeans = h2o_cmd.runKMeansOnly(parseResult=parseResult, timeoutSecs=5, **kwargs)
            (centers, tupleResultList) = h2o_kmeans.bigCheckResults(self, kmeans, csvPathname, parseResult, 'd', **kwargs)

            # check center list (first center) has same number of cols as source data
            self.assertEqual(colCount, len(centers[0]),
                "kmeans first center doesn't have same # of values as dataset row %s %s" % (colCount, len(centers[0])))

if __name__ == '__main__':
    h2o.unit_main()
