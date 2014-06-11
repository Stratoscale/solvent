import gitwrapper
import solventwrapper
import shutil
import os
import unittest
import upseto
import osmosiswrapper
import tempfile


class Test(unittest.TestCase):
    def setUp(self):
        self.osmosisPair = osmosiswrapper.LocalAndOfficial()
        gitwrapper.setUp()
        self.fixture()
        self.cleanLocalClonesDir()

    def cleanLocalClonesDir(self):
        shutil.rmtree(gitwrapper.localClonesDir())
        os.makedirs(gitwrapper.localClonesDir())

    def tearDown(self):
        gitwrapper.tearDown()
        if self.osmosisPair is not None:
            self.osmosisPair.exit()

    def fixture(self):
        self.project1 = gitwrapper.GitHub("project1")
        self.project2 = gitwrapper.GitHub("project2")
        self.requiringProject = gitwrapper.GitHub("requiringProject")

        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone2 = gitwrapper.LocalClone(self.project2)
        localRequiringProject = gitwrapper.LocalClone(self.requiringProject)
        self.assertEquals(self.project1.hash('master'), localClone1.hash())
        self.assertEquals(self.project2.hash('master'), localClone2.hash())
        self.assertEquals(self.requiringProject.hash(), localRequiringProject.hash())

        solventwrapper.upseto(localRequiringProject, "addRequirement project1")
        solventwrapper.upseto(localRequiringProject, "addRequirement project2")
        localRequiringProject.addCommitPushManifest()

        self.recursiveProject = gitwrapper.GitHub("recursiveProject")
        localRecursiveProject = gitwrapper.LocalClone(self.recursiveProject)
        solventwrapper.upseto(localRecursiveProject, "addRequirement requiringProject")
        localRecursiveProject.addCommitPushManifest()

    def test_Fixture(self):
        self.assertNotIn('/usr', upseto.__file__)
        import solvent
        self.assertNotIn('/usr', solvent.__file__)
        localRecursiveProject = gitwrapper.LocalClone(self.recursiveProject)
        solventwrapper.upseto(localRecursiveProject, "fulfillRequirements")
        lines = solventwrapper.upseto(localRecursiveProject, "checkRequirements --show")
        self.assertEquals(len([l for l in lines.split("\n") if 'file:///' in l]), 4)

    def test_SubmitANonUpsetoedProject(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        hash = localClone1.hash()
        self.assertFalse(localClone1.fileExists("build/product1"))
        localClone1.writeFile("build/product1", "product1 contents")
        self.assertTrue(localClone1.fileExists("build/product1"))

        solventwrapper.run(localClone1, "submitbuild")
        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__project1__build__%s__cleancandidate' % hash
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)
        self.assertEquals(self.osmosisPair.official.client().listLabels(), [label])

        self.cleanLocalClonesDir()
        self.assertFalse(localClone1.fileExists("build/product1"))
        self.osmosisPair.local.client().checkout(path=gitwrapper.localClonesDir(), label=label)
        self.assertEquals(localClone1.hash(), hash)
        self.assertTrue(localClone1.fileExists("build/product1"))

    def test_SubmitANonUpsetoedProject_FailsIfWorkspaceIsSullied(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        localClone2 = gitwrapper.LocalClone(self.project2)

        solventwrapper.runShouldFail(localClone1, "submitbuild", "sullied")

    def test_ConfigurationMissingOfficialOsmosis(self):
        configuration = tempfile.NamedTemporaryFile()
        solventwrapper.configurationFile = configuration.name
        localClone1 = gitwrapper.LocalClone(self.project1)
        solventwrapper.runShouldFail(localClone1, "submitbuild", "empty")

        configuration.write("key: value\n")
        configuration.flush()
        solventwrapper.runShouldFail(localClone1, "submitbuild", "official")

    def test_SubmitBuildNotAllowedFromANonGitProject(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        self.osmosisPair.exit()
        solventwrapper.runShouldFail(localClone1, "submitbuild", "osmosis")
        self.osmosisPair = None

    def test_SubmitANonUpsetoedProjectOfficialBuild(self):
        localClone1 = gitwrapper.LocalClone(self.project1)
        hash = localClone1.hash()
        localClone1.writeFile("build/product1", "product1 contents")

        solventwrapper.configureAsOfficial()
        solventwrapper.run(localClone1, "submitbuild")
        self.assertEquals(len(self.osmosisPair.local.client().listLabels()), 1)
        label = 'solvent__project1__build__%s__officialcandidate' % hash
        self.assertEquals(self.osmosisPair.local.client().listLabels(), [label])
        self.assertEquals(len(self.osmosisPair.official.client().listLabels()), 1)
        self.assertEquals(self.osmosisPair.official.client().listLabels(), [label])

        self.cleanLocalClonesDir()
        self.osmosisPair.local.client().checkout(path=gitwrapper.localClonesDir(), label=label)
        self.assertEquals(localClone1.hash(), hash)
        self.assertTrue(localClone1.fileExists("build/product1"))


#submit dirty -> publish


if __name__ == '__main__':
    unittest.main()
