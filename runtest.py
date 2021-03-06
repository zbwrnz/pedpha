#!/usr/bin/env python3
import lib.gffreader as gffreader
import pedpha
import unittest
import os

# ================
# gff_reader tests
# ================

def prepare_gff(gff, addnew=True):
    # If the input is a list of lists, join them
    if gff and not hasattr(gff[0], "strip"):
        gff = ["\t".join([str(e) for e in x]) for x in gff]

    # Actual input will always have newlines separating records
    if addnew:
        gff = [s + "\n" for s in gff]

    return(gff)

def readgff(gfflist, addnew=True):
    gff = prepare_gff(gfflist, addnew=addnew)

    out = []
    with open(os.devnull, 'w') as errout:
        for gene in gffreader.gff_reader(gff, errout=errout):
            for line in gene.tostr():
                out.append(line)
    return(out)


class Test_gffreader(unittest.TestCase):
    def setUp(self):
        self.good = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '100', '109', '.', '+', '.', 'ID=a.1.exon.1'],
            ['s1', '.', 'exon', '110', '200', '.', '+', '.', 'ID=a.1.exon.2'],
            ['s1', '.', 'CDS', '150', '200', '.', '+', '.', 'ID=a.1.cds.1'],
            ['s1', '.', 'exon', '300', '400', '.', '+', '.', 'ID=a.1.exon.3'],
            ['s1', '.', 'CDS', '300', '400', '.', '+', '.', 'ID=a.1.cds.2'],
            ['s1', '.', 'exon', '600', '900', '.', '+', '.', 'ID=a.1.exon.4'],
            ['s1', '.', 'CDS', '600', '603', '.', '+', '.', 'ID=a.1.cds.2'],
            ['s1', '.', 'exon', '910', '930', '.', '+', '.', 'ID=a.1.exon.5']
        ]
        self.good_output = [
            ['s1', 'a.1', '1', '1', '1000', '+', '1', 'a.1.exon.1', '100', '109', '.', '.', '.', '.'],
            ['s1', 'a.1', '1', '1', '1000', '+', '2', 'a.1.exon.2', '110', '200', '150', '200', '.', '0'],
            ['s1', 'a.1', '1', '1', '1000', '+', '3', 'a.1.exon.3', '300', '400', '300', '400', '0', '2'],
            ['s1', 'a.1', '1', '1', '1000', '+', '4', 'a.1.exon.4', '600', '900', '600', '603', '2', '.'],
            ['s1', 'a.1', '1', '1', '1000', '+', '5', 'a.1.exon.5', '910', '930', '.', '.', '.', '.']
        ]
        self.good_output = [' '.join(s) for s in self.good_output]

        self.minus = [
            ['s1', '.', 'gene', '1',   '1000', '.', '-', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1',   '1000', '.', '-', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '800', '900',  '.', '-', '.', 'ID=a.1.exon.1'],
            ['s1', '.', 'exon', '600', '700',  '.', '-', '.', 'ID=a.1.exon.2'],
            ['s1', '.', 'CDS',  '600', '650',  '.', '-', '.', 'ID=a.1.cds.1'],
            ['s1', '.', 'exon', '400', '500',  '.', '-', '.', 'ID=a.1.exon.3'],
            ['s1', '.', 'CDS',  '400', '500',  '.', '-', '.', 'ID=a.1.cds.2'],
            ['s1', '.', 'exon', '200', '300',  '.', '-', '.', 'ID=a.1.exon.4'],
            ['s1', '.', 'CDS',  '297', '300',  '.', '-', '.', 'ID=a.1.cds.2'],
            ['s1', '.', 'exon', '10',  '150',  '.', '-', '.', 'ID=a.1.exon.5']
        ]
        self.minus_output = [
            ['s1', 'a.1', '1', '1', '1000', '-', '1', 'a.1.exon.1', '800', '900',   '.',   '.', '.', '.'],
            ['s1', 'a.1', '1', '1', '1000', '-', '2', 'a.1.exon.2', '600', '700', '600', '650', '.', '0'],
            ['s1', 'a.1', '1', '1', '1000', '-', '3', 'a.1.exon.3', '400', '500', '400', '500', '0', '2'],
            ['s1', 'a.1', '1', '1', '1000', '-', '4', 'a.1.exon.4', '200', '300', '297', '300', '2', '.'],
            ['s1', 'a.1', '1', '1', '1000', '-', '5', 'a.1.exon.5', '10',  '150',   '.',   '.', '.', '.']
        ]
        self.minus_output = [' '.join(s) for s in self.minus_output]

    def test_good(self):
        self.assertEqual(readgff(self.good), self.good_output)

    def test_minus(self):
        self.assertEqual(readgff(self.minus), self.minus_output)

class Test_phase(unittest.TestCase):
    def test_same_interval_0_offset(self):
        self.assertEqual(gffreader.phase((1,6), (1,6), 0, True), (0,0))
        self.assertEqual(gffreader.phase((1,7), (1,7), 0, True), (0,1))
        self.assertEqual(gffreader.phase((1,8), (1,8), 0, True), (0,2))
        self.assertEqual(gffreader.phase((4,11), (4,11), 0, True), (0,2))
        self.assertEqual(gffreader.phase((4,14), (4,14), 0, True), (0,2))

    def test_same_interval_variable_offset(self):
        self.assertEqual(gffreader.phase((1,7), (1,7), 0, True), (0,1))
        self.assertEqual(gffreader.phase((1,7), (1,7), 1, True), (1,2))
        self.assertEqual(gffreader.phase((1,7), (1,7), 2, True), (2,0))
        self.assertEqual(gffreader.phase((1,7), (1,7), 3, True), (0,1))
        self.assertEqual(gffreader.phase((1,7), (1,7), 432, True), (0,1))
        self.assertEqual(gffreader.phase((1,7), (1,7), 433, True), (1,2))
        self.assertEqual(gffreader.phase((1,7), (1,7), 434, True), (2,0))
        self.assertEqual(gffreader.phase((31,37), (31,37), 434, True), (2,0))

    def test_borders_plus(self):
        self.assertEqual(gffreader.phase((1,100), (91,100), 0, True), (".",1))
        self.assertEqual(gffreader.phase((1,100), (50,61), 0, True), (".","."))
        self.assertEqual(gffreader.phase((400,500), (400,411), 1, True), (1,"."))

    def test_borders_minus(self):
        self.assertEqual(gffreader.phase((1,100), (91,100), 0, False), (0,"."))
        self.assertEqual(gffreader.phase((1,100), (50,61), 0, False), (".","."))
        self.assertEqual(gffreader.phase((400,500), (400,411), 0, False), (".",0))
        self.assertEqual(gffreader.phase((400,500), (400,412), 0, False), (".",1))

class Test_a_is_downstream_of_b(unittest.TestCase):
    def test_true_plus(self):
        self.assertTrue(gffreader.a_is_downstream_of_b(a=2, b=1, strand="+"))
        self.assertTrue(gffreader.a_is_downstream_of_b(a=2, b=2, strand="+"))
    def test_false_plus(self):
        self.assertFalse(gffreader.a_is_downstream_of_b(a=1, b=2, strand="+"))
    def test_true_minus(self):
        self.assertTrue(gffreader.a_is_downstream_of_b(a=99, b=100, strand="-"))
        self.assertTrue(gffreader.a_is_downstream_of_b(a=100, b=100, strand="-"))
    def test_false_minus(self):
        self.assertFalse(gffreader.a_is_downstream_of_b(a=100, b=99, strand="-"))
class Test_a_is_upstream_of_b(unittest.TestCase):
    def test_true_plus(self):
        self.assertTrue(gffreader.a_is_upstream_of_b(a=1, b=2, strand="+"))
        self.assertTrue(gffreader.a_is_upstream_of_b(a=2, b=2, strand="+"))
    def test_false_plus(self):
        self.assertFalse(gffreader.a_is_upstream_of_b(a=2, b=1, strand="+"))
    def test_true_minus(self):
        self.assertTrue(gffreader.a_is_upstream_of_b(a=100, b=99, strand="-"))
        self.assertTrue(gffreader.a_is_upstream_of_b(a=100, b=100, strand="-"))
    def test_false_minus(self):
        self.assertFalse(gffreader.a_is_upstream_of_b(a=99, b=100, strand="-"))
class Test_a_is_within_b(unittest.TestCase):
    def test_within(self):
        self.assertTrue(gffreader.a_is_within_b((2, 5), (1, 6)))
        self.assertTrue(gffreader.a_is_within_b((5, 2), (1, 6)))
    def test_same_interval(self):
        self.assertTrue(gffreader.a_is_within_b((1, 5), (1, 5)))
    def test_shared_boundary(self):
        self.assertTrue(gffreader.a_is_within_b((2, 5), (2, 6)))
        self.assertTrue(gffreader.a_is_within_b((2, 5), (1, 5)))
    def test_false(self):
        self.assertFalse(gffreader.a_is_within_b((2, 5), (3, 5)))
        self.assertFalse(gffreader.a_is_within_b((2, 5), (2, 4)))
        self.assertFalse(gffreader.a_is_within_b((2, 5), (3, 4)))
    def test_bound_order(self):
        self.assertTrue(gffreader.a_is_within_b((5, 2), (2, 6)))
        self.assertTrue(gffreader.a_is_within_b((2, 5), (6, 2)))

class Test_a_overlaps_b(unittest.TestCase):
    def test_true(self):
        self.assertTrue(gffreader.a_overlaps_b((1,15), (10,20)))
        self.assertTrue(gffreader.a_overlaps_b((15,30), (10,20)))
        self.assertTrue(gffreader.a_overlaps_b((1,30), (10,20)))
        self.assertTrue(gffreader.a_overlaps_b((11,19), (10,20)))
    def test_equal_border(self):
        self.assertTrue(gffreader.a_overlaps_b((10,20), (10,20)))
        self.assertTrue(gffreader.a_overlaps_b((1,10), (10,20)))
        self.assertTrue(gffreader.a_overlaps_b((20,30), (10,20)))
    def test_false(self):
        self.assertFalse(gffreader.a_overlaps_b((1,9), (10,20)))
        self.assertFalse(gffreader.a_overlaps_b((21,30), (10,20)))

class Test_format_checkint(unittest.TestCase):
    def test_misformatted_no_gene(self):
        test = [
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '100', '109', '.', '+', '.', 'ID=a.1.exon.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_mRNA_out(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1001', '.', '+', '.', 'ID=a.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_exon_out(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '100', '1001', '.', '+', '.', 'ID=a.1.exon.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_cds_out(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '100', '1001', '.', '+', '.', 'ID=a.1.exon.1'],
            ['s1', '.', 'CDS',  '30', '131',  '.', '+', '.', 'ID=a.1.cds.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_wrong_strand(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '-', '.', 'ID=a.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_no_strand(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '.', '.', 'ID=a']
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_no_mRNA(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'exon', '100', '1001', '.', '+', '.', 'ID=a.1.exon.1'],
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_CDS_without_exon(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'CDS',  '30', '131',  '.', '-', '.', 'ID=a.1.cds.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_exons_misordered_plus(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '110', '200', '.', '+', '.', 'ID=a.1.exon.2'],
            ['s1', '.', 'exon', '100', '109', '.', '+', '.', 'ID=a.1.exon.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_misformatted_overlapping_exons(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '100', '200', '.', '+', '.', 'ID=a.1.exon.1'],
            ['s1', '.', 'exon', '150', '300', '.', '+', '.', 'ID=a.1.exon.2']
        ]
        self.assertEqual(readgff(test), [])

    def test_no_gene_ident(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'a']
        ]
        self.assertEqual(readgff(test), [])

    def test_no_mRNA_ident(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'a.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_no_exon_ident(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '100', '200', '.', '+', '.', 'a.1.exon.1']
        ]
        self.assertEqual(readgff(test), [])

    def test_no_cds_ident(self):
        test = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '150', '300', '.', '+', '.', 'ID=a.1.exon.2'],
            ['s1', '.', 'CDS',  '160', '162',  '.', '+', '.', 'a.1.cds.1']
        ]
        self.assertEqual(readgff(test), [])


# ============
# pedpha tests
# ============

def ready_phaser(gfflist, intervals):
    gff = prepare_gff(gfflist)
    intervals = [s + "\n" for s in intervals]
    out = list(pedpha.phaser(gff, intervals))
    return(out)


class Test_phaser(unittest.TestCase):
    def setUp(self):
        self.gff = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '100', '109', '.', '+', '.', 'ID=a.1.e1'],
            ['s1', '.', 'exon', '110', '200', '.', '+', '.', 'ID=a.1.e2'],
            ['s1', '.', 'CDS', '150', '200', '.', '+', '.', 'ID=a.1.c1'],
            ['s1', '.', 'exon', '300', '400', '.', '+', '.', 'ID=a.1.e3'],
            ['s1', '.', 'CDS', '300', '400', '.', '+', '.', 'ID=a.1.c2'],
            ['s1', '.', 'exon', '600', '900', '.', '+', '.', 'ID=a.1.e4'],
            ['s1', '.', 'CDS', '600', '603', '.', '+', '.', 'ID=a.1.c3'],
            ['s1', '.', 'exon', '910', '930', '.', '+', '.', 'ID=a.1.e5']
        ]

        self.multigene = [
            ['s1', '.', 'gene', '1', '1000', '.', '+', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1', '1000', '.', '+', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '100', '109', '.', '+', '.', 'ID=a.1.e1'],
            ['s1', '.', 'exon', '110', '200', '.', '+', '.', 'ID=a.1.e2'],
            ['s1', '.', 'CDS', '150', '200', '.', '+', '.', 'ID=a.1.c1'],
            ['s1', '.', 'exon', '300', '400', '.', '+', '.', 'ID=a.1.e3'],
            ['s1', '.', 'CDS', '300', '400', '.', '+', '.', 'ID=a.1.c2'],
            ['s1', '.', 'exon', '600', '900', '.', '+', '.', 'ID=a.1.e4'],
            ['s1', '.', 'CDS', '600', '603', '.', '+', '.', 'ID=a.1.c3'],
            ['s1', '.', 'exon', '910', '930', '.', '+', '.', 'ID=a.1.e5'],
            ['s2', '.', 'gene', '5001', '6000', '.', '+', '.', 'ID=b'],
            ['s2', '.', 'mRNA', '5001', '6000', '.', '+', '.', 'ID=b.1'],
            ['s2', '.', 'exon', '5100', '5109', '.', '+', '.', 'ID=b.1.e1'],
            ['s2', '.', 'exon', '5110', '5200', '.', '+', '.', 'ID=b.1.e2'],
            ['s2', '.', 'CDS', '5150', '5200', '.', '+', '.', 'ID=b.1.c1'],
            ['s2', '.', 'exon', '5300', '5400', '.', '+', '.', 'ID=b.1.e3'],
            ['s2', '.', 'CDS', '5300', '5400', '.', '+', '.', 'ID=b.1.c2'],
            ['s2', '.', 'exon', '5600', '5900', '.', '+', '.', 'ID=b.1.e4'],
            ['s2', '.', 'CDS', '5600', '5603', '.', '+', '.', 'ID=b.1.c3'],
            ['s2', '.', 'exon', '5910', '5930', '.', '+', '.', 'ID=b.1.e5'],
            ['s2', '.', 'mRNA', '5001', '6000', '.', '+', '.', 'ID=b.2'],
            ['s2', '.', 'exon', '5200', '5209', '.', '+', '.', 'ID=b.2.e1'],
            ['s2', '.', 'exon', '5210', '5300', '.', '+', '.', 'ID=b.2.e2'],
            ['s2', '.', 'CDS', '5250', '5300', '.', '+', '.', 'ID=b.2.c1'],
            ['s2', '.', 'exon', '5400', '5500', '.', '+', '.', 'ID=b.2.e3'],
            ['s2', '.', 'CDS', '5400', '5500', '.', '+', '.', 'ID=b.2.c2'],
            ['s2', '.', 'exon', '5600', '5900', '.', '+', '.', 'ID=b.2.e4'],
            ['s2', '.', 'CDS', '5600', '5603', '.', '+', '.', 'ID=b.2.c3'],
            ['s2', '.', 'exon', '5910', '5930', '.', '+', '.', 'ID=b.2.e5']
        ]

        self.minus = [
            ['s1', '.', 'gene', '1',   '1000', '.', '-', '.', 'ID=a'],
            ['s1', '.', 'mRNA', '1',   '1000', '.', '-', '.', 'ID=a.1'],
            ['s1', '.', 'exon', '800', '900',  '.', '-', '.', 'ID=a.1.exon.1'],
            ['s1', '.', 'exon', '600', '700',  '.', '-', '.', 'ID=a.1.exon.2'],
            ['s1', '.', 'CDS',  '600', '650',  '.', '-', '.', 'ID=a.1.cds.1'],
            ['s1', '.', 'exon', '400', '500',  '.', '-', '.', 'ID=a.1.exon.3'],
            ['s1', '.', 'CDS',  '400', '500',  '.', '-', '.', 'ID=a.1.cds.2'],
            ['s1', '.', 'exon', '200', '300',  '.', '-', '.', 'ID=a.1.exon.4'],
            ['s1', '.', 'CDS',  '297', '300',  '.', '-', '.', 'ID=a.1.cds.2'],
            ['s1', '.', 'exon', '10',  '150',  '.', '-', '.', 'ID=a.1.exon.5']
        ]

    def test_single_exon1(self):
        self.assertEqual(ready_phaser(self.gff, ["a.1 z 1 2"]),
                         [('a.1', 2, 'z', 1, '+', 110, 200, 150, 155, 1, 6, ".-0")])

    def test_single_exon2(self):
        self.assertEqual(ready_phaser(self.gff, ["a.1 z 1 17"]),
                         [('a.1', 2, 'z', 1, '+', 110, 200, 150, 200, 1, 51, ".-0")])

    def test_single_exon3(self):
        self.assertEqual(ready_phaser(self.gff, ["a.1 z 18 20"]),
                         [( 'a.1', 3, 'z', 1, '+', 300, 400, 300, 308, 52, 60, "0-2")])

    def test_single_exon4(self):
        self.assertEqual(ready_phaser(self.gff, ["a.1 z 19 20"]),
                         [('a.1', 3, 'z', 1, '+', 300, 400, 303, 308, 55, 60, "0-2")])

    def test_multi_exon(self):
        self.assertEqual(ready_phaser(self.gff, ["a.1 z 1 18"]),
                         [('a.1', 2, 'z', 1, '+', 110, 200, 150, 200, 1, 51, ".-0"),
                          ('a.1', 3, 'z', 1, '+', 300, 400, 300, 302, 52, 54, "0-2")])

    def test_multi_gene_one_interval(self):
        self.assertEqual(ready_phaser(self.multigene, ['b.1 z 1 2']),
                         [('b.1', 2, 'z', 1, '+', 5110, 5200, 5150, 5155, 1, 6, ".-0")])

    def test_multi_gene_two_intervals(self):
        self.assertEqual(ready_phaser(self.multigene, ["a.1 z 1 2", 'b.1 z 1 2']),
                         [('a.1', 2, 'z', 1, '+', 110, 200, 150, 155, 1, 6, ".-0"),
                          ('b.1', 2, 'z', 1, '+', 5110, 5200, 5150, 5155, 1, 6, ".-0")])

    def test_multi_gene_two_intervals_one_mRNA(self):
        self.assertEqual(ready_phaser(self.multigene, ["a.1 z 1 2", "a.1 z 4 5"]),
                         [('a.1', 2, 'z', 1, '+', 110, 200, 150, 155, 1, 6, ".-0"),
                          ('a.1', 2, 'z', 2, '+', 110, 200, 159, 164, 10, 15, ".-0")])

    def test_multi_mRNA(self):
        self.assertEqual(ready_phaser(self.multigene, ['b.2 z 1 2']),
                         [('b.2', 2, 'z', 1, '+', 5210, 5300, 5250, 5255, 1, 6, ".-0")])

    def test_minus(self):
        self.assertEqual(ready_phaser(self.minus, ["a.1 z 1 2"]),
                         [('a.1', 2, 'z', 1, '-', 600, 700, 645, 650, 1, 6, ".-0")])

    def test_multi_exon_minus(self):
        self.assertEqual(ready_phaser(self.minus, ["a.1 z 2 18"]),
                         [('a.1', 2, 'z', 1, '-', 600, 700, 600, 647, 4, 51, ".-0"),
                          ('a.1', 3, 'z', 1, '-', 400, 500, 498, 500, 52, 54, "0-2")])

    def test_bad_interval(self):
        self.assertRaises(SystemExit, pedpha.Intervals, ["a.1 z 0   1\n"])
        self.assertRaises(SystemExit, pedpha.Intervals, ["a.1 z 1   0\n"])
        self.assertRaises(SystemExit, pedpha.Intervals, ["a.1 z 0.1 1\n"])
        self.assertRaises(SystemExit, pedpha.Intervals, ["a.1 z -1  1\n"])
        self.assertRaises(SystemExit, pedpha.Intervals, ["a.1 z a   1\n"])

class Test_to_dna_coor(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(pedpha.to_dna_interval([1,1]), [1,3])
        self.assertEqual(pedpha.to_dna_interval([1,2]), [1,6])
        self.assertEqual(pedpha.to_dna_interval([2,3]), [4,9])
class Test_get_overlap(unittest.TestCase):
    def test_within_plus(self):
        self.assertEqual(pedpha.get_overlap([1,5], [100, 104], minus=False), (100, 104))
        self.assertEqual(pedpha.get_overlap([1,4], [100, 104], minus=False), (100, 103))
        self.assertEqual(pedpha.get_overlap([2,4], [100, 104], minus=False), (101, 103))
        self.assertEqual(pedpha.get_overlap([2,2], [100, 104], minus=False), (101, 101))
    def test_within_minus_equal(self):
        self.assertEqual(pedpha.get_overlap([1,5], [100, 104], minus=True), (100, 104))
    def test_within_minus_within_low(self):
        self.assertEqual(pedpha.get_overlap([1,4], [100, 104], minus=True), (101, 104))
    def test_within_minus_within_mid(self):
        self.assertEqual(pedpha.get_overlap([2,4], [100, 104], minus=True), (101, 103))
        self.assertEqual(pedpha.get_overlap([2,2], [100, 104], minus=True), (103, 103))

    def test_rightwards_plus(self):
        self.assertEqual(pedpha.get_overlap([1,10], [100, 104], minus=False), (100, 104))
        self.assertEqual(pedpha.get_overlap([5,10], [100, 104], minus=False), (104, 104))
    def test_rightwards_minus(self):
        self.assertEqual(pedpha.get_overlap([1,10], [100, 104], minus=True), (100, 104))
        self.assertEqual(pedpha.get_overlap([5,10], [100, 104], minus=True), (100, 100))

    def test_beyond_plus(self):
        self.assertEqual(pedpha.get_overlap([6,10], [100, 104], minus=False), (None, None))
    def test_beyond_minus(self):
        self.assertEqual(pedpha.get_overlap([6,10], [100, 104], minus=True), (None, None))


if __name__ == '__main__':
    unittest.main()
